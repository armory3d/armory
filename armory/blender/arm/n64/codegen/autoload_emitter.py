"""
Autoload Emitter - Extends TraitEmitter for autoload classes.

Autoloads use global variables prefixed with c_name instead of a data pointer.
"""

from typing import Dict, List

from arm.n64.codegen.trait_emitter import TraitEmitter


class AutoloadEmitter(TraitEmitter):
    """Emits C code from IR nodes for autoload classes.

    Unlike traits which use a data pointer (data->member), autoloads use
    global variables prefixed with c_name (music_volume, music_play(), etc.)
    """

    def __init__(self, autoload_name: str, c_name: str, member_names: List[str], function_names: List[str], member_types: Dict[str, str] = None):
        super().__init__(autoload_name, c_name, member_names, is_trait=False)
        self.function_names = function_names
        self.member_types = member_types or {}
        self.param_types: Dict[str, str] = {}  # Populated when emitting a function

    def emit_member(self, node: Dict) -> str:
        """Autoload member access: c_name_member_name (global variable)"""
        name = node.get("value", "")
        return f"{self.c_name}_{name}"

    def _is_null_node(self, node: Dict) -> bool:
        """Check if a node is a null literal."""
        if node is None:
            return False
        return node.get("type", "") == "null"

    def _is_sound_handle(self, node: Dict) -> bool:
        """Check if a node refers to an ArmSoundHandle type."""
        if node is None:
            return False
        node_type = node.get("type", "")
        if node_type == "ident":
            name = node.get("value", "")
            return self.member_types.get(name) == "ArmSoundHandle"
        return False

    def _is_string_type(self, node: Dict) -> bool:
        """Check if a node is a string type (string literal or const char* variable)."""
        if node is None:
            return False
        node_type = node.get("type", "")
        if node_type == "string":
            return True
        if node_type == "ident":
            name = node.get("value", "")
            ctype = self.member_types.get(name) or self.param_types.get(name)
            return ctype == "const char*"
        return False

    def emit_binop(self, node: Dict) -> str:
        """Binary operator - special handling for ArmSoundHandle and string comparisons."""
        op = node.get("value", "+")
        children = node.get("children", [])
        if len(children) >= 2:
            left_node = children[0]
            right_node = children[1]

            # Check for ArmSoundHandle assignment with null
            if op == "=" and self._is_sound_handle(left_node) and self._is_null_node(right_node):
                left = self.emit(left_node)
                if left:
                    return f"({left} = (ArmSoundHandle){{-1, 0, -1, 1.0f, true}})"

            # Check for ArmSoundHandle comparison (including with null)
            if op in ("==", "!="):
                left_is_handle = self._is_sound_handle(left_node)
                right_is_handle = self._is_sound_handle(right_node)
                left_is_null = self._is_null_node(left_node)
                right_is_null = self._is_null_node(right_node)

                if (left_is_handle or right_is_handle) and (left_is_handle or right_is_handle or left_is_null or right_is_null):
                    # One side is a handle, emit comparison
                    if left_is_null:
                        left = "(ArmSoundHandle){-1, 0, -1, 1.0f, true}"
                    else:
                        left = self.emit(left_node)
                    if right_is_null:
                        right = "(ArmSoundHandle){-1, 0, -1, 1.0f, true}"
                    else:
                        right = self.emit(right_node)
                    if left and right:
                        if op == "==":
                            return f"arm_sound_handle_equals({left}, {right})"
                        else:
                            return f"!arm_sound_handle_equals({left}, {right})"

                # Check for string comparison
                if self._is_string_type(left_node) or self._is_string_type(right_node):
                    left = self.emit(left_node)
                    right = self.emit(right_node)
                    if left and right:
                        if op == "==":
                            return f"(strcmp({left}, {right}) == 0)"
                        else:
                            return f"(strcmp({left}, {right}) != 0)"

            # Fall back to base implementation
            return super().emit_binop(node)
        return ""

    def emit_ident(self, node: Dict) -> str:
        """Identifier - prefix members and functions with c_name."""
        name = node.get("value", "")
        # Check if this is a reference to one of the autoload's own members
        if name in self.member_names:
            return f"{self.c_name}_{name}"
        # Check if this is a reference to one of the autoload's own functions
        if name in self.function_names:
            return f"{self.c_name}_{name}"
        # Otherwise use base implementation
        return super().emit_ident(node)

    def emit_field_access(self, node: Dict) -> str:
        """Field access for autoloads - this.field and inst.field -> c_name_field."""
        obj_node = node.get("object")
        field = node.get("value", "")

        if obj_node:
            obj_type = obj_node.get("type", "")
            obj_value = obj_node.get("value", "")

            # Check for Assets.sounds.sound_name pattern -> ROM path
            if obj_type == "field_access" and obj_node.get("value") == "sounds":
                inner_obj = obj_node.get("object", {})
                if inner_obj.get("type") == "ident" and inner_obj.get("value") == "Assets":
                    # Convert to ROM path: "rom:/sound_name.wav64"
                    return f'"rom:/{field}.wav64"'

            # this.field or inst.field -> c_name_field (global variable)
            if obj_type == "ident" and obj_value in ("this", "inst"):
                if field in self.member_names:
                    return f"{self.c_name}_{field}"
                return field

            # Regular field access
            obj = self.emit(obj_node)
            if obj:
                return f"({obj}).{field}"

        return field

    def emit_call(self, node: Dict) -> str:
        """Function call - prefix autoload functions with c_name."""
        func_name = node.get("value", "")
        if func_name:
            # Prefix if it's one of this autoload's functions
            if func_name in self.function_names:
                func_name = f"{self.c_name}_{func_name}"
            # IR uses 'args' for call arguments
            args = node.get("args", []) or node.get("children", [])
            arg_strs = [self.emit(a) for a in args if self.emit(a)]
            return f"{func_name}({', '.join(arg_strs)})"
        return ""

    def emit_global_signal_call(self, node: Dict) -> str:
        """Global signal calls - uses c_code template from macro.

        For autoloads, the callback is a module-level function and there's
        no data pointer (unlike traits), so we pass NULL.
        Signal handlers need a wrapper for proper signature matching.
        """
        c_code = node.get("c_code", "")
        if not c_code:
            return ""

        props = node.get("props", {})
        global_signal = props.get("global_signal", "")
        callback = props.get("callback", "")

        # Build signal pointer and handler name
        signal_ptr = f"&{global_signal}"
        # Use wrapper function for signal handlers (has proper ArmSignalHandler signature)
        handler_name = f"{self.c_name}_{callback}_wrapper" if callback else ""

        # Substitute placeholders, then fix autoload-specific data pattern
        c_code = self._substitute_placeholders(
            c_code, node.get("args", []),
            signal_ptr=signal_ptr, handler=handler_name
        )
        # Autoloads don't have a data pointer, pass NULL
        c_code = c_code.replace(", data)", ", NULL)")

        return c_code

    def emit_audio_handle_field(self, node: Dict) -> str:
        """Handle field access - prefix handle name if it's a member."""
        props = node.get("props", {})
        handle_name = props.get("handle_name", "")
        field = node.get("value", "")
        if handle_name and field:
            # If handle_name is a member of this autoload, prefix it
            if handle_name in self.member_names:
                handle_name = f"{self.c_name}_{handle_name}"
            return f"{handle_name}.{field}"
        return node.get("c_code", "")
