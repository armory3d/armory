"""
N64 Code Generator - Thin IR→C Emitter.

This module provides pure 1:1 IR→C mapping. All semantic analysis,
type resolution, and event extraction happen in the Haxe macro
(N64TraitMacro.hx).

Pipeline:
  Haxe Macro (all semantics) → JSON IR → codegen.py (1:1 emit) → C code

Coordinate conversion for trait code (e.g., swizzle x,y,z → x,z,-y) and
scale factors (0.015625 for Blender→N64, 64.0 for N64→Blender) are handled
entirely in the Haxe macro via the c_code field. The emit_* functions only
substitute placeholders like {0}, {1}, {v}, {obj}. The convert_* functions
in utils.py handle static scene data export only.

The IR schema (version 1):
  {
    ir_version: 1,
    traits: {
      TraitName: {
        module: "arm.node.TraitName",
        c_name: "arm_node_traitname",
        members: [{name, type, ctype, default_value}],
        events: {event_name: [IRNode...]},
        meta: {uses_input, uses_transform, uses_time, buttons_used}
      }
    }
  }

IRNode types (1:1 with emit_* handlers):
  Literals: int, float, string, bool, null, skip
  Variables: member, ident, field, gamepad_stick
  Operators: assign, binop, unop
  Control: if, block, var, return
  Calls: call, scene_call, transform_call, math_call, input_call, physics_call, vec_call
  Utility: cast_call, debug_call, object_call
  Constructors: new

TraitMeta fields:
  uses_input, uses_transform, mutates_transform, uses_time, uses_physics,
  buttons_used: [str], button_events: [{event_name, button, c_button, event_type}]
"""

import json
import os
import math
from typing import Dict, List, Optional

from arm.n64.utils import (
    convert_vec3_list, convert_quat_list, convert_scale_list,
    SCALE_FACTOR
)


# =============================================================================
# IR Emitter - Pure 1:1 translation
# =============================================================================

class IREmitter:
    """Emits C code from IR nodes. No semantic analysis, just translation."""

    def __init__(self, trait_name: str, c_name: str, member_names: List[str]):
        self.trait_name = trait_name
        self.c_name = c_name
        self.member_names = member_names
        self.data_type = f"{trait_name}Data"

    def emit(self, node: Optional[Dict]) -> str:
        """Emit C code for an IR node."""
        if node is None:
            return ""

        node_type = node.get("type", "")
        method_name = f"emit_{node_type}"
        method = getattr(self, method_name, None)

        if method:
            return method(node)

        # Unknown node type - log for debugging
        print(f"[N64] Unknown IR node type: {node_type}")
        return ""

    def emit_list(self, nodes: List[Dict]) -> List[str]:
        """Emit list of nodes, filtering out empty results."""
        return [c for c in (self.emit(n) for n in nodes) if c]

    def emit_statements(self, nodes: List[Dict], indent: str = "    ") -> str:
        """Emit list of nodes as statements, adding semicolons where needed."""
        lines = self.emit_list(nodes)
        result = []
        for line in lines:
            # Add semicolon if line doesn't end with ; or } or is empty
            if line and not line.rstrip().endswith((';', '}', '{')):
                line = line + ';'
            result.append(f"{indent}{line}")
        return "\n".join(result)

    # =========================================================================
    # Literals
    # =========================================================================

    def emit_int(self, node: Dict) -> str:
        return str(node.get("value", 0))

    def emit_float(self, node: Dict) -> str:
        val = node.get("value", 0.0)
        # Ensure float format (e.g., 0.0f not 0f)
        val_str = str(val)
        if "." not in val_str:
            val_str = f"{val}.0"
        return f"{val_str}f"

    def emit_string(self, node: Dict) -> str:
        val = node.get("value", "")
        return f'"{val}"' if val else "NULL"

    def emit_sprintf(self, node: Dict) -> str:
        """Pre-built sprintf from macro: { type: "sprintf", value: "format", args: [...] }
        The macro has already built the format string and collected typed args.
        We just translate to C."""
        format_str = node.get("value", "")
        args = node.get("args", [])

        if not args:
            # No args, just a literal string
            return f'"{format_str}"'

        # Emit each argument
        arg_codes = [self.emit(arg) for arg in args]
        args_str = ", ".join(arg_codes)

        return f'_str_concat("{format_str}", {args_str})'

    def emit_bool(self, node: Dict) -> str:
        return "true" if node.get("value", False) else "false"

    def emit_null(self, node: Dict) -> str:
        return "NULL"

    def emit_skip(self, node: Dict) -> str:
        return ""

    # =========================================================================
    # Variables
    # =========================================================================

    def emit_member(self, node: Dict) -> str:
        """Trait member access: data->member_name"""
        name = node.get("value", "")
        return f"(({self.data_type}*)data)->{name}"

    def emit_ident(self, node: Dict) -> str:
        """Identifier: local var, dt, object, etc."""
        name = node.get("value", "")
        if name == "object":
            return "((ArmObject*)obj)"
        if name == "dt":
            return "dt"
        return name

    def emit_field(self, node: Dict) -> str:
        """Field access: object.field or vec.x"""
        obj = self.emit(node.get("object"))
        field = node.get("value", "")

        if not obj:
            return field

        # Transform field access
        if "transform." in field:
            subfield = field.replace("transform.", "")
            return f"{obj}->transform.{subfield}"

        # Object pointer access (ArmObject*, etc.)
        if "ArmObject*" in obj or "ArmCamera*" in obj or "ArmLight*" in obj:
            return f"{obj}->{field}"

        return f"({obj}).{field}"

    def emit_label_field(self, node: Dict) -> str:
        """Label field access: label->pos_x, label->text, etc.
        The macro has already mapped Koui names (posX) to C names (pos_x)."""
        obj = self.emit(node.get("object"))
        field = node.get("value", "")
        if obj and field:
            return f"{obj}->{field}"
        return ""

    def emit_gamepad_stick(self, node: Dict) -> str:
        """Gamepad stick access: returns ArmVec2 with x,y from input functions."""
        stick = node.get("value", "leftStick")
        # Generate inline struct - input functions return floats
        return "(ArmVec2){input_stick_x(), input_stick_y()}"

    # =========================================================================
    # Operators
    # =========================================================================

    def emit_assign(self, node: Dict) -> str:
        """Assignment: target = value;"""
        children = node.get("children", [])
        if len(children) >= 2:
            target = self.emit(children[0])
            value = self.emit(children[1])
            if target and value:
                return f"{target} = {value};"
        return ""

    def emit_binop(self, node: Dict) -> str:
        """Binary operator: left op right"""
        op = node.get("value", "+")
        children = node.get("children", [])
        if len(children) >= 2:
            left = self.emit(children[0])
            right = self.emit(children[1])
            if left and right:
                # Compound assignments are statements, need semicolon
                if op in ("+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="):
                    return f"{left} {op} {right};"
                return f"({left} {op} {right})"
        return ""

    def emit_unop(self, node: Dict) -> str:
        """Unary operator: ++x or x++"""
        op = node.get("value", "!")
        children = node.get("children", [])
        props = node.get("props", {})
        postfix = props.get("postfix", False)

        if children:
            operand = self.emit(children[0])
            if operand:
                if postfix:
                    return f"({operand}{op})"
                return f"({op}{operand})"
        return ""

    # =========================================================================
    # Control Flow
    # =========================================================================

    def emit_if(self, node: Dict) -> str:
        """If statement."""
        children = node.get("children", [])
        props = node.get("props", {})

        if not children:
            return ""

        cond = self.emit(children[0])
        if not cond:
            return ""

        then_nodes = props.get("then", [])
        then_code = self.emit_statements(then_nodes, "        ")

        result = f"if ({cond}) {{\n{then_code}\n    }}"

        else_nodes = props.get("else_")
        if else_nodes:
            else_code = self.emit_statements(else_nodes, "        ")
            result += f" else {{\n{else_code}\n    }}"

        return result

    def emit_block(self, node: Dict) -> str:
        """Block of statements - emit as statements with semicolons."""
        children = node.get("children", [])
        # Use emit_statements logic but without extra indent (caller handles indent)
        lines = self.emit_list(children)
        result = []
        for line in lines:
            # Add semicolon if line doesn't end with ; or } or {
            if line and not line.rstrip().endswith((';', '}', '{')):
                line = line + ';'
            result.append(line)
        return "\n".join(result)

    def emit_var(self, node: Dict) -> str:
        """Local variable declaration: ctype name = value;"""
        name = node.get("value", "")
        props = node.get("props", {})
        children = node.get("children", [])
        ctype = props.get("ctype", "float")

        if children and len(children) > 0:
            val = self.emit(children[0])
            if val:
                return f"{ctype} {name} = {val};"
        return f"{ctype} {name};"

    def emit_return(self, node: Dict) -> str:
        """Return statement: return value; or just return;"""
        children = node.get("children", [])
        if children and len(children) > 0:
            val = self.emit(children[0])
            if val:
                return f"return {val};"
        return "return;"

    # =========================================================================
    # Function Calls
    # =========================================================================

    def emit_call(self, node: Dict) -> str:
        """Unhandled call - add pattern to macro."""
        method = node.get("method", "")
        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args if self.emit(a)]

        if method:
            print(f"[N64 codegen] WARNING: Unhandled call '{method}' - add to macro")
            return f"{method}({', '.join(arg_strs)})"
        return ""

    def emit_scene_call(self, node: Dict) -> str:
        """Scene.setActive() -> scene_switch_to()"""
        if "c_code" in node:
            return node["c_code"] + ";"
        args = node.get("args", [])
        if args:
            scene_expr = self.emit(args[0])
            return f"scene_switch_to(scene_get_id_by_name({scene_expr}));"
        return ""

    def emit_transform_call(self, node: Dict) -> str:
        """Transform calls - substitute placeholders in macro-provided c_code."""
        c_code = node.get("c_code", "")
        if not c_code:
            return ""

        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args]

        # Substitute {0}, {1}, {2}, etc. with emitted args
        # Provide default "1.0f" for missing optional args (e.g., move scale)
        for i in range(10):
            placeholder = "{" + str(i) + "}"
            if placeholder in c_code:
                val = arg_strs[i] if i < len(arg_strs) else "1.0f"
                c_code = c_code.replace(placeholder, val)

        return c_code

    def emit_math_call(self, node: Dict) -> str:
        """Math.sin() -> sinf(), etc."""
        c_func = node.get("value", "")
        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args if self.emit(a)]
        return f"{c_func}({', '.join(arg_strs)})"

    def emit_input_call(self, node: Dict) -> str:
        """Input calls - macro provides C code."""
        return node.get("c_code", "0")

    def emit_physics_call(self, node: Dict) -> str:
        """Physics calls - substitute placeholders in macro-provided c_code."""
        c_code = node.get("c_code", "")
        if not c_code:
            return ""

        obj_node = node.get("object")
        args = node.get("args", [])

        # Get object expression
        obj = self.emit(obj_node) if obj_node else "((ArmObject*)obj)"

        # Emit args
        arg_strs = [self.emit(a) for a in args]

        # Substitute {obj} and {0}, {1}, etc.
        c_code = c_code.replace("{obj}", obj)
        for i, arg in enumerate(arg_strs):
            c_code = c_code.replace("{" + str(i) + "}", arg)

        return c_code

    def emit_koui_call(self, node: Dict) -> str:
        """Koui UI calls - pure 1:1 translation from macro-provided c_func."""
        c_func = node.get("c_func", "")
        args = node.get("args", [])
        obj_node = node.get("object")

        if not c_func:
            print("[N64 codegen] WARNING: koui_call missing c_func")
            return ""

        # Build argument list: object first (if present), then args
        arg_strs = []
        if obj_node:
            obj = self.emit(obj_node)
            if obj:
                arg_strs.append(obj)

        for a in args:
            emitted = self.emit(a)
            if emitted:
                arg_strs.append(emitted)

        return f"{c_func}({', '.join(arg_strs)})"

    def emit_signal_call(self, node: Dict) -> str:
        """Signal calls - connect/disconnect/emit on per-instance signals.

        Generates calls to signal_* functions that operate on ArmSignal structs
        stored in trait data.
        """
        action = node.get("value", "")  # "connect", "disconnect", or "emit"
        props = node.get("props", {})
        signal_name = props.get("signal_name", "")

        if not signal_name:
            return ""

        # Signal is stored in trait data: data->signalName
        signal_ptr = f"&(({self.data_type}*)data)->{signal_name}"

        if action == "connect":
            callback = props.get("callback", "")
            if callback:
                # signal_connect(signal, handler, obj, data)
                # The callback function must be defined - use c_name prefix
                handler_name = f"{self.c_name}_{callback}"
                return f"signal_connect({signal_ptr}, {handler_name}, obj, data);"
            return ""

        elif action == "disconnect":
            callback = props.get("callback", "")
            if callback:
                handler_name = f"{self.c_name}_{callback}"
                return f"signal_disconnect({signal_ptr}, {handler_name});"
            return ""

        elif action == "emit":
            args = node.get("args", [])
            arg_strs = [self.emit(a) for a in args]
            arg_count = len(arg_strs)

            # Use convenience macros for correct argument count (max 4 args)
            if arg_count == 0:
                return f"signal_emit0({signal_ptr}, obj);"
            elif arg_count == 1:
                return f"signal_emit1({signal_ptr}, obj, {arg_strs[0]});"
            elif arg_count == 2:
                return f"signal_emit2({signal_ptr}, obj, {arg_strs[0]}, {arg_strs[1]});"
            elif arg_count == 3:
                return f"signal_emit3({signal_ptr}, obj, {arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]});"
            else:
                # 4 or more args - use first 4
                return f"signal_emit4({signal_ptr}, obj, {arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]}, {arg_strs[3]});"

        return ""

    def emit_global_signal_call(self, node: Dict) -> str:
        """Global signal calls - GameEvents.signalName.connect/emit/disconnect.

        Global signals are stored as extern ArmSignal structs.
        """
        action = node.get("value", "")
        props = node.get("props", {})
        global_signal = props.get("global_signal", "")

        if not global_signal:
            return ""

        signal_ptr = f"&{global_signal}"

        if action == "connect":
            callback = props.get("callback", "")
            if callback:
                handler_name = f"{self.c_name}_{callback}"
                return f"signal_connect({signal_ptr}, {handler_name}, obj, data);"
            return ""

        elif action == "disconnect":
            callback = props.get("callback", "")
            if callback:
                handler_name = f"{self.c_name}_{callback}"
                return f"signal_disconnect({signal_ptr}, {handler_name});"
            return ""

        elif action == "emit":
            args = node.get("args", [])
            arg_strs = [self.emit(a) for a in args]
            arg_count = len(arg_strs)

            if arg_count == 0:
                return f"signal_emit0({signal_ptr}, obj);"
            elif arg_count == 1:
                return f"signal_emit1({signal_ptr}, obj, {arg_strs[0]});"
            elif arg_count == 2:
                return f"signal_emit2({signal_ptr}, obj, {arg_strs[0]}, {arg_strs[1]});"
            elif arg_count == 3:
                return f"signal_emit3({signal_ptr}, obj, {arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]});"
            else:
                return f"signal_emit4({signal_ptr}, obj, {arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]}, {arg_strs[3]});"

        return ""

    def emit_cast_call(self, node: Dict) -> str:
        """Std.int() -> (int32_t)value"""
        cast = node.get("value", "(int32_t)")
        args = node.get("args", [])
        if args:
            return f"{cast}({self.emit(args[0])})"
        return ""

    def emit_debug_call(self, node: Dict) -> str:
        """trace() -> debugf()"""
        args = node.get("args", [])
        if not args:
            return 'debugf("")'
        arg_strs = [self.emit(a) for a in args if self.emit(a)]
        if len(arg_strs) == 1:
            return f'debugf("%s\\n", {arg_strs[0]})'
        return f'debugf("{", ".join(["%s"] * len(arg_strs))}\\n", {", ".join(arg_strs)})'

    def emit_object_call(self, node: Dict) -> str:
        """Object calls - return macro-provided c_code."""
        return node.get("c_code", "")

    def emit_vec_call(self, node: Dict) -> str:
        """Vec calls - substitute placeholders in macro-provided c_code."""
        c_code = node.get("c_code", "")
        if not c_code:
            return ""

        obj_node = node.get("object")
        args = node.get("args", [])

        # Get the vector object
        obj = self.emit(obj_node) if obj_node else ""
        if not obj:
            return ""

        # Emit args
        arg_strs = [self.emit(a) for a in args]

        # Determine if we need parentheses around obj
        is_compound = obj.startswith("(Arm")
        v = f"({obj})" if is_compound else obj

        # Substitute placeholders
        c_code = c_code.replace("{v}", v)
        c_code = c_code.replace("{vraw}", obj)  # Raw var name for normalize
        for i, arg in enumerate(arg_strs):
            c_code = c_code.replace("{" + str(i) + "}", arg)

        return c_code

    # =========================================================================
    # Constructors
    # =========================================================================

    def emit_new(self, node: Dict) -> str:
        """Constructor calls: new Vec3(x, y, z) or new Vec4(x, y, z, w)"""
        type_name = node.get("value", "")
        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args]

        if type_name == "Vec4":
            # Vec4 with 4 args: full quaternion/4D vector
            if len(arg_strs) >= 4:
                return f"(ArmVec4){{{arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]}, {arg_strs[3]}}}"
            # Vec4 with 3 args: treat as Vec3 position (w=1.0 for homogeneous coords)
            if len(arg_strs) >= 3:
                return f"(ArmVec4){{{arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]}, 1.0f}}"
            return "(ArmVec4){0, 0, 0, 1.0f}"

        if type_name == "Vec3":
            if len(arg_strs) >= 3:
                return f"(ArmVec3){{{arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]}}}"
            return "(ArmVec3){0, 0, 0}"

        if type_name == "Vec2":
            if len(arg_strs) >= 2:
                return f"(ArmVec2){{{arg_strs[0]}, {arg_strs[1]}}}"
            return "(ArmVec2){0, 0}"

        return ""


# =============================================================================
# Trait Code Generator
# =============================================================================

class TraitCodeGenerator:
    """Generates C code for a single trait from IR.

    Pure 1:1 emitter - all data comes from macro-generated IR.
    """

    def __init__(self, name: str, ir: Dict, type_overrides: Dict = None):
        self.name = name
        self.c_name = ir.get("c_name", "")  # Must be provided by macro
        self.members = ir.get("members", [])
        self.events = ir.get("events", {})
        self.meta = ir.get("meta", {})
        self.type_overrides = type_overrides or {}

        member_names = [m.get("name") for m in self.members]
        self.emitter = IREmitter(name, self.c_name, member_names)

    def _get_member_ctype(self, member: Dict) -> str:
        """Get the C type for a member, applying overrides if present."""
        name = member.get("name", "unknown")
        ctype = member.get("ctype", "float")
        # Apply type override if present
        if self.name in self.type_overrides:
            if name in self.type_overrides[self.name]:
                ctype = self.type_overrides[self.name][name]
        return ctype

    def generate_data_struct(self) -> str:
        """Generate the data struct for trait members and signals."""
        signals = self.meta.get("signals", [])

        if not self.members and not signals:
            return ""

        lines = [f"typedef struct {{"]

        # Regular members
        for m in self.members:
            ctype = self._get_member_ctype(m)
            name = m.get("name", "unknown")
            lines.append(f"    {ctype} {name};")

        # Signal members - each signal is an ArmSignal struct
        for sig in signals:
            sig_name = sig.get("name", "")
            if sig_name:
                lines.append(f"    ArmSignal {sig_name};")

        lines.append(f"}} {self.name}Data;")

        return "\n".join(lines)

    def generate_lifecycle_declarations(self) -> List[str]:
        """Generate declarations for lifecycle event handlers."""
        decls = []
        # Match the typedefs in types.h:
        # ArmTraitReadyFn: (void *entity, void *data) - no dt
        # ArmTraitFixedUpdateFn: (void *entity, float dt, void *data)
        # ArmTraitUpdateFn: (void *entity, float dt, void *data)
        # ArmTraitLateUpdateFn: (void *entity, float dt, void *data)
        # ArmTraitRemoveFn: (void *entity, void *data) - no dt
        decls.append(f"void {self.c_name}_on_ready(void* obj, void* data);")
        decls.append(f"void {self.c_name}_on_fixed_update(void* obj, float dt, void* data);")
        decls.append(f"void {self.c_name}_on_update(void* obj, float dt, void* data);")
        decls.append(f"void {self.c_name}_on_late_update(void* obj, float dt, void* data);")
        decls.append(f"void {self.c_name}_on_remove(void* obj, void* data);")
        return decls

    def generate_button_event_declarations(self) -> List[str]:
        """Generate declarations for button event handlers."""
        decls = []
        for event_name in self.events.keys():
            if event_name.startswith("btn_"):
                # Button events use TraitEventHandler signature: (obj, data, dt)
                decls.append(f"void {self.c_name}_{event_name}(void* obj, void* data, float dt);")
        return decls

    def generate_contact_event_declarations(self) -> List[str]:
        """Generate declarations for contact event handlers."""
        decls = []
        for event_name in self.events.keys():
            if event_name.startswith("contact_"):
                # Contact events use PhysicsContactHandler signature: (obj, data, other)
                decls.append(f"void {self.c_name}_{event_name}(void* obj, void* data, ArmObject* other);")
        return decls

    def generate_signal_handler_declarations(self) -> List[str]:
        """Generate declarations for signal handler callbacks - reads from events."""
        decls = []
        for event_name in self.events.keys():
            if event_name.startswith("signal_"):
                handler_name = event_name[7:]  # Strip "signal_" prefix
                # ArmSignalHandler signature: void (*)(void* obj, void* data, void* arg0, void* arg1, void* arg2, void* arg3)
                decls.append(f"void {self.c_name}_{handler_name}(void* obj, void* data, void* arg0, void* arg1, void* arg2, void* arg3);")
        return decls

    def generate_all_event_implementations(self) -> str:
        """Generate C implementations for all event handlers."""
        impl_lines = [f"// ========== {self.name} =========="]

        # on_ready - no dt parameter
        event_nodes = self.events.get("on_ready", [])
        body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
        impl_lines.append(f"void {self.c_name}_on_ready(void* obj, void* data) {{")
        impl_lines.append(body)
        impl_lines.append("}")
        impl_lines.append("")

        # on_fixed_update - dt before data (ArmTraitFixedUpdateFn)
        event_nodes = self.events.get("on_fixed_update", [])
        body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
        impl_lines.append(f"void {self.c_name}_on_fixed_update(void* obj, float dt, void* data) {{")
        impl_lines.append(body)
        impl_lines.append("}")
        impl_lines.append("")

        # on_update - dt before data (ArmTraitUpdateFn)
        event_nodes = self.events.get("on_update", [])
        body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
        impl_lines.append(f"void {self.c_name}_on_update(void* obj, float dt, void* data) {{")
        impl_lines.append(body)
        impl_lines.append("}")
        impl_lines.append("")

        # on_late_update - dt before data (ArmTraitLateUpdateFn)
        event_nodes = self.events.get("on_late_update", [])
        body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
        impl_lines.append(f"void {self.c_name}_on_late_update(void* obj, float dt, void* data) {{")
        impl_lines.append(body)
        impl_lines.append("}")
        impl_lines.append("")

        # on_remove - no dt parameter
        event_nodes = self.events.get("on_remove", [])
        body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
        impl_lines.append(f"void {self.c_name}_on_remove(void* obj, void* data) {{")
        impl_lines.append(body)
        impl_lines.append("}")
        impl_lines.append("")

        # Button events - data before dt (TraitEventHandler signature)
        for event_name in self.events.keys():
            if event_name.startswith("btn_"):
                event_nodes = self.events.get(event_name, [])
                body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
                impl_lines.append(f"void {self.c_name}_{event_name}(void* obj, void* data, float dt) {{")
                impl_lines.append(body)
                impl_lines.append("}")
                impl_lines.append("")

        # Contact events - PhysicsContactHandler signature: (obj, data, other)
        for event_name in self.events.keys():
            if event_name.startswith("contact_"):
                event_nodes = self.events.get(event_name, [])
                body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
                impl_lines.append(f"void {self.c_name}_{event_name}(void* obj, void* data, ArmObject* other) {{")
                impl_lines.append(f"    (void)other;  // Available as 'other' in body if needed")
                impl_lines.append(body)
                impl_lines.append("}")
                impl_lines.append("")

        # Signal handler events - ArmSignalHandler signature: (obj, data, arg0, arg1, arg2, arg3)
        for event_name in self.events.keys():
            if event_name.startswith("signal_"):
                event_nodes = self.events.get(event_name, [])
                body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
                handler_name = event_name[7:]  # Strip "signal_" prefix
                impl_lines.append(f"void {self.c_name}_{handler_name}(void* obj, void* data, void* arg0, void* arg1, void* arg2, void* arg3) {{")
                impl_lines.append(f"    (void)arg0; (void)arg1; (void)arg2; (void)arg3;  // Signal args")
                impl_lines.append(body)
                impl_lines.append("}")
                impl_lines.append("")

        return "\n".join(impl_lines)


# =============================================================================
# JSON Loading Utilities
# =============================================================================

def load_traits_json(build_dir: str = None) -> dict:
    """
    Load the n64_traits.json file generated by the macro.

    Args:
        build_dir: Build directory path (defaults to arm.utils.build_dir())

    Returns:
        Parsed JSON dict with ir_version and traits
    """
    import os
    import arm.utils

    if build_dir is None:
        build_dir = arm.utils.build_dir()

    possible_paths = [
        os.path.join(build_dir, "n64_traits.json"),
        os.path.join(build_dir, "build", "n64_traits.json"),
        os.path.join(build_dir, "debug", "n64_traits.json"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    version = data.get("ir_version", 0)
                    if version != 1:
                        print(f"[N64] Warning: Expected IR version 1, got {version}")
                    return data
            except Exception as e:
                print(f"[N64] Error loading {path}: {e}")

    return {"ir_version": 0, "traits": {}}


def get_trait_info(build_dir: str = None) -> dict:
    """
    Load traits JSON and return in expected format.

    This is the main entry point for other code to get trait info.
    Returns dict with:
        ir_version: Schema version
        traits: {TraitName: {module, c_name, members, events, meta}}
    """
    return load_traits_json(build_dir)


# =============================================================================
# Scene Data Conversion
# =============================================================================

def convert_scene_data(scene_data: dict) -> dict:
    """Apply coordinate conversion to all scene data (modifies in place).

    Converts from Blender coordinates (X=right, Y=forward, Z=up)
    to N64/T3D coordinates (X=right, Y=up, Z=back).
    """
    for scene_name, scene in scene_data.items():
        # Convert cameras
        for cam in scene.get('cameras', []):
            cam['pos'] = convert_vec3_list(cam['pos'])
            cam['target'] = convert_vec3_list(cam['target'])

        # Convert lights
        for light in scene.get('lights', []):
            light['dir'] = convert_vec3_list(light['dir'])
            # Normalize direction
            d = light['dir']
            length = math.sqrt(d[0]**2 + d[1]**2 + d[2]**2)
            if length > 0:
                light['dir'] = [d[0]/length, d[1]/length, d[2]/length]

        # Convert objects
        for obj in scene.get('objects', []):
            obj['pos'] = convert_vec3_list(obj['pos'])
            obj['rot'] = convert_quat_list(obj['rot'])
            obj['scale'] = convert_scale_list(obj['scale'])
            if 'bounds_center' in obj:
                obj['bounds_center'] = convert_vec3_list(obj['bounds_center'])
                obj['bounds_radius'] = obj['bounds_radius'] * SCALE_FACTOR

    return scene_data


# =============================================================================
# Traits File Generation
# =============================================================================

def write_traits_files(type_overrides: dict = None):
    """Generate traits.h and traits.c from IR JSON using templates.

    Args:
        type_overrides: Optional dict of {trait_name: {member_name: ctype}} overrides

    Returns:
        dict with feature flags: {'has_ui': bool, 'has_physics': bool}
    """
    import arm.utils

    build_dir = arm.utils.build_dir()
    data = load_traits_json(build_dir)
    traits = data.get("traits", {})

    if not traits:
        print("[N64] No traits to generate")
        return {'has_ui': False, 'has_physics': False}

    data_dir = os.path.join(build_dir, "n64", "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    tmpl_dir = os.path.join(arm.utils.get_n64_deployment_path(), "src", "data")

    # Generate template substitution data and detect features
    template_data, features = _prepare_traits_template_data(traits, type_overrides)

    # Generate traits.h from template
    h_tmpl_path = os.path.join(tmpl_dir, "traits.h.j2")
    h_path = os.path.join(data_dir, "traits.h")
    with open(h_tmpl_path, 'r') as f:
        h_template = f.read()
    h_content = h_template.format(**template_data)
    with open(h_path, 'w') as f:
        f.write(h_content)

    # Generate traits.c from template
    c_tmpl_path = os.path.join(tmpl_dir, "traits.c.j2")
    c_path = os.path.join(data_dir, "traits.c")
    with open(c_tmpl_path, 'r') as f:
        c_template = f.read()
    c_content = c_template.format(**template_data)
    with open(c_path, 'w') as f:
        f.write(c_content)

    print(f"[N64] Generated {h_path} and {c_path}")
    return features


def _detect_features_in_nodes(nodes) -> dict:
    """Recursively scan IR nodes for feature usage (UI, physics, etc.)."""
    features = {'has_ui': False, 'has_physics': False}

    def scan(node):
        if not node or not isinstance(node, dict):
            return
        node_type = node.get("type", "")
        if node_type == "koui_call" or node_type == "label_field":
            features['has_ui'] = True
        elif node_type == "physics_call":
            features['has_physics'] = True

        # Recursively scan children and args
        for child in node.get("children", []):
            scan(child)
        for arg in node.get("args", []):
            scan(arg)
        if node.get("object"):
            scan(node["object"])

    if isinstance(nodes, list):
        for n in nodes:
            scan(n)
    elif isinstance(nodes, dict):
        scan(nodes)

    return features


def _prepare_traits_template_data(traits: dict, type_overrides: dict = None) -> tuple:
    """Prepare data for traits.h.j2 and traits.c.j2 templates.

    Uses TraitCodeGenerator for each trait to avoid code duplication.

    Returns:
        tuple of (template_data dict, features dict)
    """
    trait_data_structs = []
    trait_declarations = []
    event_handler_declarations = []
    trait_implementations = []
    global_signals = set()  # Collect unique global signals

    # Track features across all traits
    all_features = {'has_ui': False, 'has_physics': False}

    for trait_name, trait_ir in traits.items():
        gen = TraitCodeGenerator(trait_name, trait_ir, type_overrides)

        # Header data: struct + declarations
        struct = gen.generate_data_struct()
        if struct:
            trait_data_structs.append(struct)

        trait_declarations.extend(gen.generate_lifecycle_declarations())
        event_handler_declarations.extend(gen.generate_button_event_declarations())
        event_handler_declarations.extend(gen.generate_contact_event_declarations())
        event_handler_declarations.extend(gen.generate_signal_handler_declarations())

        # Collect global signals from this trait
        meta = trait_ir.get("meta", {})
        for gs in meta.get("global_signals", []):
            global_signals.add(gs)

        # Implementation data
        trait_implementations.append(gen.generate_all_event_implementations())

        # Detect features in events
        events = trait_ir.get("events", {})
        for event_name, event_nodes in events.items():
            node_features = _detect_features_in_nodes(event_nodes)
            if node_features['has_ui']:
                all_features['has_ui'] = True
            if node_features['has_physics']:
                all_features['has_physics'] = True

        # Check members for UI types (e.g., KouiLabel*)
        members = trait_ir.get("members", [])
        for m in members:
            ctype = m.get("ctype", "")
            if "Koui" in ctype or "Label" in ctype:
                all_features['has_ui'] = True

    # Generate global signal declarations with explicit zero initialization
    global_signal_decls = []
    for gs in sorted(global_signals):
        global_signal_decls.append(f"ArmSignal {gs} = {{0}};")

    template_data = {
        "trait_data_structs": "\n\n".join(trait_data_structs),
        "trait_declarations": "\n".join(trait_declarations),
        "event_handler_declarations": "\n".join(event_handler_declarations),
        "trait_implementations": "\n".join(trait_implementations),
        "global_signals": "\n".join(global_signal_decls),
    }

    return template_data, all_features


# =============================================================================
# Scene Generation - These combine Blender data with trait IR
# =============================================================================

def _fmt_vec3(v: List[float]) -> str:
    """Format a 3-element list as T3DVec3 initializer."""
    return f'(T3DVec3){{{{ {v[0]:.6f}f, {v[1]:.6f}f, {v[2]:.6f}f }}}}'


def generate_transform_block(prefix: str, pos: List[float],
                             rot: List[float] = None,
                             scale: List[float] = None,
                             is_static: bool = False) -> List[str]:
    """Generate C code for transform initialization."""
    lines = []
    lines.append(f'    {prefix}.transform.loc = (T3DVec3){{{{{pos[0]:.6f}f, {pos[1]:.6f}f, {pos[2]:.6f}f}}}};')

    if rot:
        lines.append(f'    {prefix}.transform.rot = (T3DQuat){{{{{rot[0]:.6f}f, {rot[1]:.6f}f, {rot[2]:.6f}f, {rot[3]:.6f}f}}}};')

    if scale:
        lines.append(f'    {prefix}.transform.scale = (T3DVec3){{{{{scale[0]:.6f}f, {scale[1]:.6f}f, {scale[2]:.6f}f}}}};')
        dirty_count = "1" if is_static else "FB_COUNT"
        lines.append(f'    {prefix}.transform.dirty = {dirty_count};')

    return lines


def generate_trait_block(prefix: str, traits: List[Dict],
                         trait_info: dict, scene_name: str) -> List[str]:
    """Generate C code for trait initialization on an object.

    Pure 1:1 emitter - all data comes from macro-generated trait_info.
    """
    from arm.n64 import utils as n64_utils

    lines = []
    lines.append(f'    {prefix}.trait_count = {len(traits)};')

    if len(traits) > 0:
        lines.append(f'    {prefix}.traits = malloc(sizeof(ArmTrait) * {len(traits)});')

        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]

            # Get trait IR - must exist, macro provides all data
            trait_ir = trait_info.get("traits", {}).get(trait_class, {})
            c_name = trait_ir.get("c_name", "")
            meta = trait_ir.get("meta", {})

            # Lifecycle hooks - use the full c_name
            lines.append(f'    {prefix}.traits[{t_idx}].on_ready = {c_name}_on_ready;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_fixed_update = {c_name}_on_fixed_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_update = {c_name}_on_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_late_update = {c_name}_on_late_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_remove = {c_name}_on_remove;')

            # Trait data
            if n64_utils.trait_needs_data(trait_info, trait_class):
                struct_name = f'{trait_class}Data'
                instance_props = trait.get("props", {})
                type_overrides = trait.get("type_overrides", {})
                initializer = n64_utils.build_trait_initializer(
                    trait_info, trait_class, scene_name, instance_props, type_overrides
                )
                lines.append(f'    {prefix}.traits[{t_idx}].data = malloc(sizeof({struct_name}));')
                lines.append(f'    *({struct_name}*){prefix}.traits[{t_idx}].data = ({struct_name}){{{initializer}}};')
            else:
                lines.append(f'    {prefix}.traits[{t_idx}].data = NULL;')

            # Subscribe to button events using structured metadata from macro
            for btn_evt in meta.get("button_events", []):
                event_name = btn_evt.get("event_name", "")
                c_button = btn_evt.get("c_button", "N64_BTN_A")
                event_type = btn_evt.get("event_type", "started")

                handler_name = f"{c_name}_{event_name}"
                obj_ptr = f"&{prefix}" if not prefix.startswith("&") else prefix
                data_ptr = f"{prefix}.traits[{t_idx}].data"

                lines.append(f'    trait_events_subscribe_{event_type}({c_button}, {handler_name}, {obj_ptr}, {data_ptr});')

            # Note: Contact event subscriptions are generated separately in generate_contact_subscriptions_block
            # after physics bodies are created
    else:
        lines.append(f'    {prefix}.traits = NULL;')

    return lines


def generate_camera_block(cameras: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for all cameras in a scene."""
    lines = []
    for i, cam in enumerate(cameras):
        prefix = f'cameras[{i}]'
        lines.extend(generate_transform_block(prefix, cam["pos"]))
        lines.append(f'    {prefix}.target = {_fmt_vec3(cam["target"])};')
        lines.append(f'    {prefix}.fov = {cam["fov"]:.6f}f;')
        lines.append(f'    {prefix}.near = {cam["near"]:.6f}f;')
        lines.append(f'    {prefix}.far = {cam["far"]:.6f}f;')

        lines.extend(generate_trait_block(prefix, cam.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_light_block(lights: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for all lights in a scene."""
    from arm.n64 import utils as n64_utils

    lines = []
    for i, light in enumerate(lights):
        prefix = f'lights[{i}]'
        lines.append(f'    {prefix}.color[0] = {n64_utils.to_uint8(light["color"][0])};')
        lines.append(f'    {prefix}.color[1] = {n64_utils.to_uint8(light["color"][1])};')
        lines.append(f'    {prefix}.color[2] = {n64_utils.to_uint8(light["color"][2])};')
        lines.append(f'    {prefix}.dir = {_fmt_vec3(light["dir"])};')

        lines.extend(generate_trait_block(prefix, light.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_object_block(objects: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for all objects in a scene."""
    lines = []

    for i, obj in enumerate(objects):
        prefix = f'objects[{i}]'
        is_static = obj.get("is_static", False)
        lines.extend(generate_transform_block(prefix, obj["pos"], obj["rot"], obj["scale"], is_static))
        lines.append(f'    models_get({obj["mesh"]});')
        lines.append(f'    {prefix}.dpl = models_get_dpl({obj["mesh"]});')
        mat_count = "1" if is_static else "FB_COUNT"
        lines.append(f'    {prefix}.model_mat = malloc_uncached(sizeof(T3DMat4FP) * {mat_count});')
        lines.append(f'    {prefix}.visible = {str(obj["visible"]).lower()};')
        lines.append(f'    {prefix}.is_static = {str(is_static).lower()};')
        lines.append(f'    {prefix}.is_removed = false;')

        bc = obj.get("bounds_center", [0, 0, 0])
        br = obj.get("bounds_radius", 1.0)
        pos = obj["pos"]
        scale = obj["scale"]
        lines.append(f'    {prefix}.bounds_center = {_fmt_vec3(bc)};')
        lines.append(f'    {prefix}.bounds_radius = {br:.6f}f;')

        # Initialize cached world bounds (will be updated when transform.dirty > 0)
        world_center = [pos[0] + bc[0], pos[1] + bc[1], pos[2] + bc[2]]
        max_scale = max(scale[0], scale[1], scale[2])
        world_radius = br * max_scale
        lines.append(f'    {prefix}.cached_world_center = {_fmt_vec3(world_center)};')
        lines.append(f'    {prefix}.cached_world_radius = {world_radius:.6f}f;')

        lines.append(f'    {prefix}.rigid_body = NULL;')

        lines.extend(generate_trait_block(prefix, obj.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_physics_block(objects: List[Dict], world_data: dict) -> str:
    """Generate C code for physics initialization."""
    lines = []

    gravity = world_data.get("gravity", [0, 0, -9.81])
    n64_gravity = convert_vec3_list(gravity)
    lines.append(f'    physics_set_gravity({n64_gravity[0]:.6f}f, {n64_gravity[1]:.6f}f, {n64_gravity[2]:.6f}f);')
    lines.append('')

    # Physics debug drawing (from Blender's Debug Drawing panel)
    debug_mode = world_data.get("physics_debug_mode", 0)
    if debug_mode != 0:
        lines.append(f'    // Physics debug drawing (from Blender Debug Drawing panel)')
        lines.append(f'    physics_debug_init();')
        lines.append(f'    physics_debug_set_mode({debug_mode});')
        lines.append(f'    physics_debug_enable(true);')
        lines.append('')

    for i, obj in enumerate(objects):
        rb = obj.get("rigid_body")
        if rb is None:
            continue

        prefix = f'objects[{i}]'
        obj_name = obj.get("name", f"object_{i}")

        # Extract all physics parameters
        mass = rb.get("mass", 1.0)
        friction = rb.get("friction", 0.5)
        restitution = rb.get("restitution", 0.0)
        linear_damping = rb.get("linear_damping", 0.04)
        angular_damping = rb.get("angular_damping", 0.1)
        is_kinematic = rb.get("is_kinematic", False)
        is_trigger = rb.get("is_trigger", False)
        use_deactivation = rb.get("use_deactivation", True)
        col_group = rb.get("collision_group", 1)
        col_mask = rb.get("collision_mask", 1)

        # Determine rigid body type:
        # - mass == 0 means static (Blender PASSIVE type)
        # - is_kinematic means kinematic
        # - otherwise dynamic
        if mass == 0.0:
            rb_type = "OIMO_RIGID_BODY_STATIC"
        elif is_kinematic:
            rb_type = "OIMO_RIGID_BODY_KINEMATIC"
        else:
            rb_type = "OIMO_RIGID_BODY_DYNAMIC"

        shape = rb.get("shape", "box")

        lines.append(f'    // Rigid body for {obj_name}')
        lines.append('    {')
        lines.append(f'        PhysicsBodyParams params = physics_body_params_default();')
        lines.append(f'        params.mass = {mass:.6f}f;')
        lines.append(f'        params.friction = {friction:.6f}f;')
        lines.append(f'        params.restitution = {restitution:.6f}f;')
        lines.append(f'        params.linear_damping = {linear_damping:.6f}f;')
        lines.append(f'        params.angular_damping = {angular_damping:.6f}f;')
        lines.append(f'        params.collision_group = {col_group};')
        lines.append(f'        params.collision_mask = {col_mask};')
        lines.append(f'        params.animated = {"true" if is_kinematic else "false"};')
        lines.append(f'        params.trigger = {"true" if is_trigger else "false"};')
        lines.append(f'        params.use_deactivation = {"true" if use_deactivation else "false"};')

        if shape == "box":
            half_extents = rb.get("half_extents", [0.5, 0.5, 0.5])
            hx, hy, hz = half_extents[0], half_extents[1], half_extents[2]
            lines.append(f'        physics_create_box_full(&{prefix}, {rb_type}, {hx:.6f}f, {hy:.6f}f, {hz:.6f}f, &params);')
        elif shape == "sphere":
            r = rb.get("radius", 0.5)
            lines.append(f'        physics_create_sphere_full(&{prefix}, {rb_type}, {r:.6f}f, &params);')
        elif shape == "capsule":
            r = rb.get("radius", 0.5)
            hh = rb.get("half_height", 0.5)
            lines.append(f'        physics_create_capsule_full(&{prefix}, {rb_type}, {r:.6f}f, {hh:.6f}f, &params);')
        elif shape == "mesh":
            mesh_data = rb.get("mesh_data", {})
            vertices = mesh_data.get("vertices", [])
            indices = mesh_data.get("indices", [])
            num_vertices = mesh_data.get("num_vertices", len(vertices))
            index_count = len(indices)

            if vertices and indices:
                # Generate static arrays using OimoVec3 for vertices
                lines.append(f'        static OimoVec3 {obj_name}_col_verts[] = {{')
                for v_idx, v in enumerate(vertices):
                    comma = ',' if v_idx < len(vertices) - 1 else ''
                    lines.append(f'            {{{v[0]:.6f}f, {v[1]:.6f}f, {v[2]:.6f}f}}{comma}')
                lines.append('        };')
                lines.append(f'        static int16_t {obj_name}_col_indices[] = {{')
                for t_idx in range(0, len(indices), 6):
                    end_idx = min(t_idx + 6, len(indices))
                    idx_str = ', '.join(str(indices[j]) for j in range(t_idx, end_idx))
                    comma = ',' if end_idx < len(indices) else ''
                    lines.append(f'            {idx_str}{comma}')
                lines.append('        };')
                lines.append(f'        physics_create_mesh_full(&{prefix}, {obj_name}_col_verts, {obj_name}_col_indices, {num_vertices}, {index_count}, &params);')
            else:
                # Fallback to box if mesh data is missing
                lines.append(f'        physics_create_box_full(&{prefix}, {rb_type}, 0.5f, 0.5f, 0.5f, &params);')
        else:
            # Default to box
            lines.append(f'        physics_create_box_full(&{prefix}, {rb_type}, 0.5f, 0.5f, 0.5f, &params);')

        lines.append('    }')
        lines.append('')

    return '\n'.join(lines)


def generate_contact_subscriptions_block(objects: List[Dict], trait_info: dict) -> str:
    """Generate physics contact subscription calls after physics bodies exist.

    This must be called AFTER physics bodies are created, so the rigid_body
    pointers are valid when subscribing.

    Pure 1:1 emitter - handler_name comes directly from macro's contact_events.
    """
    lines = []
    has_subscriptions = False

    for i, obj in enumerate(objects):
        traits = obj.get("traits", [])
        prefix = f'objects[{i}]'

        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]
            trait_ir = trait_info.get("traits", {}).get(trait_class, {})
            meta = trait_ir.get("meta", {})

            for contact_evt in meta.get("contact_events", []):
                handler_name = contact_evt.get("handler_name", "")
                is_subscribe = contact_evt.get("subscribe", True)

                if is_subscribe and handler_name:
                    if not has_subscriptions:
                        lines.append('    // Physics contact event subscriptions')
                        has_subscriptions = True

                    obj_ptr = f"&{prefix}" if not prefix.startswith("&") else prefix
                    data_ptr = f"{prefix}.traits[{t_idx}].data"
                    lines.append(f'    physics_contact_subscribe({prefix}.rigid_body, {handler_name}, {obj_ptr}, {data_ptr});')

    if not has_subscriptions:
        return ""

    return '\n'.join(lines)


def generate_scene_traits_block(traits: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for scene-level traits.

    Pure 1:1 emitter - all data comes from macro-generated trait_info.
    """
    if not traits:
        return "    // No scene-level traits"

    lines = []
    lines.append(f'    static ArmTrait scene_traits[{len(traits)}];')

    for i, trait in enumerate(traits):
        trait_class = trait["class_name"]

        # Get trait IR - must exist, macro provides all data
        trait_ir = trait_info.get("traits", {}).get(trait_class, {})
        c_name = trait_ir.get("c_name", "")
        meta = trait_ir.get("meta", {})

        lines.append(f'    scene_traits[{i}].on_ready = {c_name}_on_ready;')
        lines.append(f'    scene_traits[{i}].on_fixed_update = {c_name}_on_fixed_update;')
        lines.append(f'    scene_traits[{i}].on_update = {c_name}_on_update;')
        lines.append(f'    scene_traits[{i}].on_late_update = {c_name}_on_late_update;')
        lines.append(f'    scene_traits[{i}].on_remove = {c_name}_on_remove;')

        from arm.n64 import utils as n64_utils
        if n64_utils.trait_needs_data(trait_info, trait_class):
            struct_name = f'{trait_class}Data'
            instance_props = trait.get("props", {})
            type_overrides = trait.get("type_overrides", {})
            initializer = n64_utils.build_trait_initializer(
                trait_info, trait_class, scene_name, instance_props, type_overrides
            )
            lines.append(f'    scene_traits[{i}].data = malloc(sizeof({struct_name}));')
            lines.append(f'    *({struct_name}*)scene_traits[{i}].data = ({struct_name}){{{initializer}}};')
        else:
            lines.append(f'    scene_traits[{i}].data = NULL;')

        # Subscribe to button events using structured metadata from macro
        for btn_evt in meta.get("button_events", []):
            event_name = btn_evt.get("event_name", "")
            c_button = btn_evt.get("c_button", "N64_BTN_A")
            event_type = btn_evt.get("event_type", "started")

            handler_name = f"{c_name}_{event_name}"
            lines.append(f'    trait_events_subscribe_{event_type}({c_button}, {handler_name}, scene, scene_traits[{i}].data);')

    lines.append(f'    scene->traits = scene_traits;')
    return '\n'.join(lines)
