"""
Tween Helper - Shared tween callback utilities for N64 code generation.

This module provides common functions for finding and generating tween
callback functions, used by both trait_generator.py and autoload_generator.py.
"""

from typing import List, Dict, Set, Tuple, Optional, Callable


def find_tween_callbacks(nodes: List[dict]) -> List[dict]:
    """Recursively find all tween callback definitions in IR nodes.

    Searches for tween_float, tween_vec4, and tween_delay nodes which have
    callback info in their props.on_update and props.on_done fields.
    Each callback info contains:
    - callback_name: The generated C function name
    - callback_type: "float", "vec4", or "done"
    - body: List of IR nodes for the callback body
    - param_name: The parameter name in the callback

    Args:
        nodes: List of IR nodes to search

    Returns:
        List of tween callback info dicts
    """
    callbacks = []
    for node in nodes:
        if node is None:
            continue
        node_type = node.get("type")

        # Check for tween nodes that contain callbacks in their props
        if node_type in ("tween_float", "tween_vec4", "tween_delay"):
            props = node.get("props", {})
            on_update = props.get("on_update")
            on_done = props.get("on_done")
            if on_update and isinstance(on_update, dict) and on_update.get("callback_name"):
                callbacks.append(on_update)
            if on_done and isinstance(on_done, dict) and on_done.get("callback_name"):
                callbacks.append(on_done)

        # Recurse into children
        children = node.get("children", [])
        if children:
            callbacks.extend(find_tween_callbacks(children))
        # Recurse into args
        args = node.get("args", [])
        if args:
            callbacks.extend(find_tween_callbacks(args))
        # Recurse into props.then / props.else_ (if statements)
        props = node.get("props", {})
        if props:
            then_nodes = props.get("then", [])
            if then_nodes:
                callbacks.extend(find_tween_callbacks(then_nodes))
            else_nodes = props.get("else_", [])
            if else_nodes:
                callbacks.extend(find_tween_callbacks(else_nodes))
        # Recurse into object
        obj = node.get("object")
        if obj and isinstance(obj, dict):
            callbacks.extend(find_tween_callbacks([obj]))
    return callbacks


def find_all_idents(nodes: List[dict]) -> Set[str]:
    """Recursively find all identifier names used in IR nodes.

    Used to detect which variables are captured in closures.

    Args:
        nodes: List of IR nodes to search

    Returns:
        Set of identifier names
    """
    idents = set()
    for node in nodes:
        if node is None:
            continue
        if node.get("type") == "ident":
            name = node.get("value", "")
            if name:
                idents.add(name)
        # Recurse into all potential child locations
        children = node.get("children", [])
        if children:
            idents.update(find_all_idents(children))
        args = node.get("args", [])
        if args:
            idents.update(find_all_idents(args))
        props = node.get("props", {})
        if props:
            then_nodes = props.get("then", [])
            if then_nodes:
                idents.update(find_all_idents(then_nodes))
            else_nodes = props.get("else_", [])
            if else_nodes:
                idents.update(find_all_idents(else_nodes))
        obj = node.get("object")
        if obj and isinstance(obj, dict):
            idents.update(find_all_idents([obj]))
    return idents


def generate_tween_callback(
    callback_info: dict,
    emitter,
    c_name: str = "",
    is_trait: bool = True
) -> str:
    """Generate a static C callback function for a tween.

    For traits, callbacks can access the trait data via the 'data' pointer.
    For autoloads, callbacks use global state with optional captured params.

    Args:
        callback_info: Dict with callback_name, callback_type, body, param_name, captures
        emitter: The code emitter to use for generating C code from IR
        c_name: The C name prefix (for autoload capture globals)
        is_trait: Whether this is a trait callback (affects data pointer handling)

    Returns:
        C code string for the callback function
    """
    if not callback_info:
        return ""

    cb_name = callback_info.get("callback_name", "")
    cb_type = callback_info.get("callback_type", "")
    body_nodes = callback_info.get("body", [])
    param_name = callback_info.get("param_name") or "v"  # Handle null from JSON
    captures = callback_info.get("captures", [])

    if not cb_name or not body_nodes:
        return ""

    lines = []

    # Build param captures map for autoloads
    param_captures = {}
    if not is_trait and captures:
        param_captures = {
            c["name"]: f"{c_name}_capture_{c['name']}"
            for c in captures if c.get("is_param", False)
        }

    # Generate function signature based on callback type
    if cb_type == "float":
        lines.append(f"static void {cb_name}_float(float {param_name}, void* obj, void* data) {{")
        if is_trait:
            lines.append("    (void)obj;")
        else:
            lines.append("    (void)obj; (void)data;")
    elif cb_type == "vec4":
        lines.append(f"static void {cb_name}_vec4(ArmVec4* {param_name}, void* obj, void* data) {{")
        if is_trait:
            lines.append("    (void)obj;")
        else:
            lines.append("    (void)obj; (void)data;")
    elif cb_type == "done":
        lines.append(f"static void {cb_name}_done(void* obj, void* data) {{")
        if is_trait:
            lines.append("    (void)obj;")
        else:
            lines.append("    (void)obj; (void)data;")
    else:
        return ""

    # For autoloads with param captures, create a wrapper emitter
    if not is_trait and param_captures:
        emitter = _CaptureEmitter(emitter, param_captures)

    # Emit body
    for node in body_nodes:
        code = emitter.emit(node)
        if code and code != "":
            for line in code.split('\n'):
                if line.strip():
                    if not line.strip().endswith((';', '{', '}')):
                        lines.append(f"    {line};")
                    else:
                        lines.append(f"    {line}")

    lines.append("}")
    return "\n".join(lines)


class _CaptureEmitter:
    """Wrapper emitter that substitutes captured params with their globals."""

    def __init__(self, base_emitter, param_captures: dict):
        self.base = base_emitter
        self.param_captures = param_captures

    def emit(self, node):
        if node is None:
            return ""
        # Intercept ident nodes that are captured params
        if node.get("type") == "ident":
            name = node.get("value", "")
            if name in self.param_captures:
                return self.param_captures[name]
        # For other nodes, use emit_with_capture_substitution
        return self._emit_with_capture_substitution(node)

    def _emit_with_capture_substitution(self, node):
        if node is None:
            return ""
        node_type = node.get("type", "")

        # For ident nodes, substitute captured params
        if node_type == "ident":
            name = node.get("value", "")
            if name in self.param_captures:
                return self.param_captures[name]
            return self.base.emit(node)

        # For method_call, handle the object specially
        if node_type == "method_call":
            obj = node.get("object")
            method = node.get("method", "")
            args = node.get("args", [])

            # Check if object is a captured param
            if obj and obj.get("type") == "ident":
                obj_name = obj.get("value", "")
                if obj_name in self.param_captures:
                    captured_obj = self.param_captures[obj_name]
                    arg_strs = [self.emit(a) for a in args]
                    # Handle audio methods
                    if method == "stop":
                        return f"arm_audio_stop(&{captured_obj})"
                    elif method == "play":
                        return f"arm_audio_start(&{captured_obj})"
                    # Fallback
                    return f"{captured_obj}.{method}({', '.join(arg_strs)})"

        # Default: use base emitter
        return self.base.emit(node)


def collect_callback_captures(
    callbacks: List[dict],
    func_params: Dict[str, str],
    member_names: Set[str],
    c_name: str
) -> Tuple[List[dict], Dict[str, List[Tuple[str, str]]]]:
    """Analyze callbacks and detect which function params they capture.

    For each callback, checks if any identifiers in its body reference
    function parameters (not members, not the callback's own param).

    Args:
        callbacks: List of tween callback info dicts
        func_params: Map of function parameter names to their C types
        member_names: Set of class member names (to exclude from captures)
        c_name: The C name prefix for this class

    Returns:
        Tuple of (updated_callbacks, callback_param_captures)
        - updated_callbacks: Callbacks with captures field populated
        - callback_param_captures: Map of callback_name to list of (param_name, ctype)
    """
    callback_param_captures = {}

    for cb in callbacks:
        cb_name = cb.get("callback_name", "")
        cb_body = cb.get("body", [])
        idents = find_all_idents(cb_body)

        # Find which idents are function params (not members, not callback param)
        cb_param_name = cb.get("param_name") or ""
        param_caps = []
        for ident_name in idents:
            if ident_name in func_params and ident_name != cb_param_name:
                if ident_name not in member_names:
                    param_caps.append((ident_name, func_params[ident_name]))

        if param_caps:
            # Store in the callback's captures
            existing_captures = cb.get("captures", [])
            for pname, pctype in param_caps:
                existing_captures.append({
                    "name": pname,
                    "type": pctype,
                    "is_member": False,
                    "is_param": True,
                    "ctype": pctype
                })
            cb["captures"] = existing_captures
            callback_param_captures[cb_name] = param_caps

    return callbacks, callback_param_captures


def generate_capture_globals(
    callback_param_captures: Dict[str, List[Tuple[str, str]]],
    c_name: str
) -> List[str]:
    """Generate static global variables for captured function parameters.

    Args:
        callback_param_captures: Map of callback_name to list of (param_name, ctype)
        c_name: The C name prefix for this class

    Returns:
        List of C global variable declaration lines
    """
    lines = []
    seen = set()

    for cb_name, param_caps in callback_param_captures.items():
        for pname, pctype in param_caps:
            global_name = f"{c_name}_capture_{pname}"
            if global_name not in seen:
                seen.add(global_name)
                lines.append(f"static {pctype} {global_name};")

    return lines
