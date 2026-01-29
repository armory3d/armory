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
  Literals: int, float, string, bool, null, skip, c_literal
  Variables: member, ident, field
  Operators: assign, binop, unop
  Control: if, block, var, return
  Calls: call, scene_call, transform_call, math_call, input_call, physics_call, vec_call
  Calls: signal_call, global_signal_call, global_signal_emit
  Utility: cast_call, debug_call, object_call, sprintf, remove_object
  Constructors: new, new_vec

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
    SCALE_FACTOR, get_trait
)
from arm.n64 import utils as n64_utils


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

    def _substitute_placeholders(self, c_code: str, args: List[Dict] = None,
                                  obj: str = None, vec: str = None,
                                  vec_raw: str = None, **extra) -> str:
        """Substitute placeholders in c_code template.

        Handles standard placeholders:
            {0}, {1}, ... - argument substitution (emitted)
            {obj} - object reference
            {v} - vector with parens
            {vraw} - vector without parens

        Extra keyword args are substituted as {key} -> value.
        """
        if args:
            arg_strs = [self.emit(a) for a in args]
            for i, arg in enumerate(arg_strs):
                c_code = c_code.replace("{" + str(i) + "}", arg)

        if obj is not None:
            c_code = c_code.replace("{obj}", obj)

        if vec is not None:
            c_code = c_code.replace("{v}", vec)

        if vec_raw is not None:
            c_code = c_code.replace("{vraw}", vec_raw)

        for key, value in extra.items():
            c_code = c_code.replace("{" + key + "}", value)

        return c_code

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

    def emit_literal(self, node: Dict) -> str:
        """Emit a literal value based on its type."""
        value = node.get("value", "")
        props = node.get("props", {})
        literal_type = props.get("literal_type", "")

        if literal_type == "float":
            # Ensure float format with f suffix
            val_str = str(value)
            if "." not in val_str:
                val_str = f"{val_str}.0"
            return f"{val_str}f"
        elif literal_type == "int":
            return str(value)
        elif literal_type == "string":
            return f'"{value}"'
        elif literal_type == "bool":
            return "true" if value == "true" else "false"
        elif literal_type == "null":
            return "NULL"
        else:
            return str(value)

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

    def emit_field_access(self, node: Dict) -> str:
        """Field access: object.field, vec.x, this.field, etc."""
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

            # this.field -> member access (for traits: data->field)
            if obj_type == "ident" and obj_value == "this":
                if field in self.member_names:
                    return f"(({self.data_type}*)data)->{field}"
                return field

            # inst.field -> also a member access for singleton patterns
            if obj_type == "ident" and obj_value == "inst":
                if field in self.member_names:
                    return f"(({self.data_type}*)data)->{field}"
                return field

            # Emit object and access field
            obj = self.emit(obj_node)
            if obj:
                # Transform field access: object->transform.loc
                if "transform." in field:
                    subfield = field.replace("transform.", "")
                    return f"{obj}->transform.{subfield}"

                # Object pointer access (ArmObject*, etc.)
                if "ArmObject*" in obj or "ArmCamera*" in obj or "ArmLight*" in obj:
                    return f"{obj}->{field}"

                return f"({obj}).{field}"

        return field

    def emit_c_literal(self, node: Dict) -> str:
        """Literal C code from macro - pure 1:1."""
        return node.get("c_code", "")

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
        """Function call - handles generic calls with value + args from macro."""
        func_name = node.get("value", "")
        if func_name:
            # IR uses 'args' for call arguments
            args = node.get("args", []) or node.get("children", [])
            arg_strs = [self.emit(a) for a in args if self.emit(a)]
            return f"{func_name}({', '.join(arg_strs)})"
        return ""

    def emit_scene_call(self, node: Dict) -> str:
        """Scene.setActive() -> scene_switch_to()"""
        if "c_code" in node:
            return node["c_code"] + ";"
        args = node.get("args", [])
        if args:
            # Runtime lookup by name string
            scene_expr = self.emit(args[0])
            return f"scene_switch_to(scene_get_id_by_name({scene_expr}));"
        return ""

    def emit_canvas_get_label(self, node: Dict) -> str:
        """canvas.getElementAs(Label, "key") -> canvas_get_label(UI_LABEL_{KEY})

        Uses the label key to build the define name. Canvas-independent since
        each scene loads its own canvas into the same label pool with matching indices.
        """
        import arm.utils
        props = node.get("props", {})
        label_key = props.get("key", "")
        if not label_key:
            return "NULL"

        safe_key = arm.utils.safesrc(label_key).upper()
        return f"canvas_get_label(UI_LABEL_{safe_key})"

    def emit_label_set_text(self, node: Dict) -> str:
        """label.text = value -> ui_label_set_text(label, value)"""
        props = node.get("props", {})
        label_name = props.get("label", "")
        args = node.get("args", [])

        if not label_name or not args:
            return ""

        # Check if this is a member variable (stored in data struct) or local variable
        if label_name in self.member_names:
            label_expr = f"(({self.data_type}*)data)->{label_name}"
        else:
            label_expr = label_name

        value = self.emit(args[0])
        return f"ui_label_set_text({label_expr}, {value});"

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
        """Math.sin() -> sinf(), etc. - use c_code if available."""
        c_code = node.get("c_code", "")
        if c_code:
            return self._substitute_placeholders(c_code, node.get("args", []))
        # Fallback for simple math calls
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
        obj = self.emit(obj_node) if obj_node else "((ArmObject*)obj)"

        return self._substitute_placeholders(c_code, node.get("args", []), obj=obj)

    def emit_signal_call(self, node: Dict) -> str:
        """Signal calls - connect/disconnect/emit on per-instance signals.

        Uses c_code template from macro with placeholder substitution.
        """
        c_code = node.get("c_code", "")
        if not c_code:
            return ""

        props = node.get("props", {})
        signal_name = props.get("signal_name", "")
        callback = props.get("callback", "")

        # Build signal pointer
        signal_ptr = f"&(({self.data_type}*)data)->{signal_name}"
        handler_name = f"{self.c_name}_{callback}" if callback else ""
        struct_type = f"{self.c_name}_{signal_name}_payload_t"

        return self._substitute_placeholders(
            c_code, node.get("args", []),
            signal_ptr=signal_ptr, handler=handler_name, struct_type=struct_type
        )

    def emit_global_signal_call(self, node: Dict) -> str:
        """Global signal calls - uses c_code template from macro."""
        c_code = node.get("c_code", "")
        if not c_code:
            return ""

        props = node.get("props", {})
        global_signal = props.get("global_signal", "")
        callback = props.get("callback", "")

        # Build signal pointer and handler name
        signal_ptr = f"&{global_signal}"
        handler_name = f"{self.c_name}_{callback}" if callback else ""

        return self._substitute_placeholders(
            c_code, node.get("args", []),
            signal_ptr=signal_ptr, handler=handler_name
        )

    def emit_autoload_call(self, node: Dict) -> str:
        """Autoload function call - ClassName.method() -> classname_method(args)."""
        props = node.get("props", {})
        c_name = props.get("c_name", "")
        method = props.get("method", "")

        if not c_name or not method:
            return ""

        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args]

        return f"{c_name}_{method}({', '.join(arg_strs)})"

    def emit_autoload_field(self, node: Dict) -> str:
        """Autoload field access - ClassName.field -> classname_field."""
        props = node.get("props", {})
        c_name = props.get("c_name", "")
        field = props.get("field", "")

        if not c_name or not field:
            return ""

        return f"{c_name}_{field}"

    def emit_remove_object(self, node: Dict) -> str:
        """Remove object call - substitute {obj} placeholder."""
        c_code = node.get("c_code", "")
        if not c_code:
            return ""

        obj_node = node.get("object")
        obj = self.emit(obj_node) if obj_node else "object"
        c_code = c_code.replace("{obj}", obj)

        return c_code

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
        obj = self.emit(obj_node) if obj_node else ""
        if not obj:
            return ""

        # Determine if we need parentheses around obj
        is_compound = obj.startswith("(Arm")
        vec = f"({obj})" if is_compound else obj

        return self._substitute_placeholders(c_code, node.get("args", []), vec=vec, vec_raw=obj)

    # =========================================================================
    # Constructors
    # =========================================================================

    def emit_new(self, node: Dict) -> str:
        """Generic constructor - fallback for non-Vec types."""
        # Vec constructors are now handled by emit_new_vec
        return ""

    def emit_new_vec(self, node: Dict) -> str:
        """Vec constructor with c_code template from macro."""
        c_code = node.get("c_code", "")
        if not c_code:
            return ""
        return self._substitute_placeholders(c_code, node.get("args", []))

    # =========================================================================
    # Audio Calls - emit audio nodes from AudioCallConverter
    # =========================================================================

    def emit_audio_play(self, node: Dict) -> str:
        """Audio play call - emit args through emitter for proper prefixing."""
        props = node.get("props", {})
        args = node.get("args", [])

        # Get sound path - either from args or c_code
        if args:
            sound_path = self.emit(args[0])
        else:
            # Fallback to c_code if present
            c_code = node.get("c_code", "")
            if c_code:
                return c_code
            sound_path = '"rom:/sound.wav64"'

        mix_channel = props.get("mix_channel", "AUDIO_MIX_MASTER")
        loop = props.get("loop", "false")

        return f"arm_audio_play({sound_path}, {mix_channel}, {loop})"

    def emit_audio_mix_volume(self, node: Dict) -> str:
        """Mix channel volume set - emit args through emitter for proper prefixing."""
        props = node.get("props", {})
        channel = props.get("channel", "AUDIO_MIX_MASTER")
        volume_str = props.get("volume", "1.0f")

        # If volume is an identifier, emit it to get proper prefixing
        # Check if it looks like an identifier (no operators, quotes, or parens)
        if volume_str and not any(c in volume_str for c in '"()+-*/=<>'):
            # It's likely a variable name - emit through ident to get prefixing
            if volume_str in self.member_names:
                # For traits: data->volume, for autoloads: c_name_volume
                volume_str = self.emit({"type": "ident", "value": volume_str})

        return f"arm_audio_set_mix_volume({channel}, {volume_str})"

    def emit_audio_mix_volume_get(self, node: Dict) -> str:
        """Mix channel volume get."""
        return node.get("c_code", "")

    def emit_audio_handle_play(self, node: Dict) -> str:
        """Handle play - emit handle with proper prefixing."""
        children = node.get("children", [])
        if children:
            handle = self.emit(children[0])
            return f"arm_audio_replay(&{handle})"
        return node.get("c_code", "")

    def emit_audio_handle_stop(self, node: Dict) -> str:
        """Handle stop - emit handle with proper prefixing."""
        children = node.get("children", [])
        if children:
            handle = self.emit(children[0])
            return f"arm_audio_stop(&{handle})"
        return node.get("c_code", "")

    def emit_audio_handle_pause(self, node: Dict) -> str:
        """Handle pause - uses stop since libdragon lacks pause."""
        children = node.get("children", [])
        if children:
            handle = self.emit(children[0])
            return f"arm_audio_stop(&{handle})"
        return node.get("c_code", "")

    def emit_audio_handle_volume(self, node: Dict) -> str:
        """Handle volume set - emit handle with proper prefixing."""
        children = node.get("children", [])
        args = node.get("args", [])
        if children:
            handle = self.emit(children[0])
            vol = "1.0f"
            if args:
                vol = self.emit(args[0])
            return f"arm_audio_set_volume(&{handle}, {vol})"
        return node.get("c_code", "")

    def emit_audio_handle_field(self, node: Dict) -> str:
        """Handle field access (e.g., handle.finished).

        For autoloads, the handle_name in props needs to be prefixed with c_name_
        if it's a member. The AutoloadIREmitter overrides this method.
        """
        props = node.get("props", {})
        handle_name = props.get("handle_name", "")
        field = node.get("value", "")
        if handle_name and field:
            return f"{handle_name}.{field}"
        return node.get("c_code", "")


# =============================================================================
# Autoload IR Emitter - Extends IREmitter for autoload classes
# =============================================================================

class AutoloadIREmitter(IREmitter):
    """Emits C code from IR nodes for autoload classes.

    Unlike traits which use a data pointer (data->member), autoloads use
    global variables prefixed with c_name (music_volume, music_play(), etc.)
    """

    def __init__(self, autoload_name: str, c_name: str, member_names: List[str], function_names: List[str], member_types: Dict[str, str] = None):
        super().__init__(autoload_name, c_name, member_names)
        self.function_names = function_names
        self.member_types = member_types or {}

    def emit_member(self, node: Dict) -> str:
        """Autoload member access: c_name_member_name (global variable)"""
        name = node.get("value", "")
        return f"{self.c_name}_{name}"

    def _is_sound_handle(self, node: Dict) -> bool:
        """Check if a node refers to an ArmSoundHandle type."""
        if node is None:
            return False
        node_type = node.get("type", "")
        if node_type == "ident":
            name = node.get("value", "")
            return self.member_types.get(name) == "ArmSoundHandle"
        return False

    def emit_binop(self, node: Dict) -> str:
        """Binary operator - special handling for ArmSoundHandle comparisons."""
        op = node.get("value", "+")
        children = node.get("children", [])
        if len(children) >= 2:
            left_node = children[0]
            right_node = children[1]

            # Check for ArmSoundHandle comparison
            if op in ("==", "!=") and (self._is_sound_handle(left_node) or self._is_sound_handle(right_node)):
                left = self.emit(left_node)
                right = self.emit(right_node)
                if left and right:
                    if op == "==":
                        return f"arm_sound_handle_equals({left}, {right})"
                    else:
                        return f"!arm_sound_handle_equals({left}, {right})"

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

    def generate_signal_payload_structs(self) -> str:
        """Generate payload struct types for signals with 2+ args.

        Uses struct_def from macro-generated metadata.
        """
        signals = self.meta.get("signals", [])
        lines = []

        for sig in signals:
            struct_def = sig.get("struct_def")
            if struct_def:
                lines.append(struct_def)
                lines.append("")

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
                # ArmSignalHandler signature: void (*)(void* ctx, void* payload)
                decls.append(f"void {self.c_name}_{handler_name}(void* ctx, void* payload);")
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

        # Signal handler events - use preamble from macro
        signal_handlers = self.meta.get("signal_handlers", [])

        for event_name in self.events.keys():
            if event_name.startswith("signal_"):
                event_nodes = self.events.get(event_name, [])
                body = self.emitter.emit_statements(event_nodes, "    ") if event_nodes else "    // Empty"
                handler_name = event_name[7:]  # Strip "signal_" prefix

                # Find preamble from signal_handlers meta
                # Default includes data cast so handler body can use 'data'
                default_preamble = f"{self.name}Data* data = ({self.name}Data*)ctx; (void)payload;"
                preamble = default_preamble
                for sh in signal_handlers:
                    if sh.get("handler_name") == handler_name:
                        preamble = sh.get("preamble", default_preamble)
                        break

                impl_lines.append(f"void {self.c_name}_{handler_name}(void* ctx, void* payload) {{")
                impl_lines.append(f"    {preamble}")
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

def prepare_traits_template_data(type_overrides: dict = None):
    """Prepare template data for traits.h and traits.c generation.

    Args:
        type_overrides: Optional dict of {trait_name: {member_name: ctype}} overrides

    Returns:
        tuple of (template_data dict, features dict) or (None, None) if no traits
    """
    import arm.utils

    build_dir = arm.utils.build_dir()

    # Load traits from Haxe macro JSON
    data = load_traits_json(build_dir)
    traits = data.get("traits", {})

    if not traits:
        return None, {'has_physics': False, 'has_ui': False}

    # Generate template substitution data and detect features
    return _prepare_traits_template_data(traits, type_overrides)


def _detect_features_in_nodes(nodes) -> dict:
    """Recursively scan IR nodes for feature usage (physics, etc.)."""
    features = {'has_physics': False}

    def scan(node):
        if not node or not isinstance(node, dict):
            return
        node_type = node.get("type", "")
        if node_type == "physics_call":
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

    Args:
        traits: Dict of trait_name -> trait_ir from JSON
        type_overrides: Optional dict of {trait_name: {member_name: ctype}} overrides

    Returns:
        tuple of (template_data dict, features dict)
    """
    import arm.utils

    trait_data_structs = []
    trait_declarations = []
    event_handler_declarations = []
    trait_implementations = []
    global_signals = set()  # Collect unique global signals

    # Track features across all traits
    all_features = {'has_physics': False, 'has_ui': False}

    for trait_name, trait_ir in traits.items():
        gen = TraitCodeGenerator(trait_name, trait_ir, type_overrides)

        # Header data: signal payload structs + data struct + declarations
        payload_structs = gen.generate_signal_payload_structs()
        if payload_structs:
            trait_data_structs.append(payload_structs)

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

        # Check if this trait uses UI
        if meta.get("uses_ui"):
            all_features['has_ui'] = True

        # Implementation data
        trait_implementations.append(gen.generate_all_event_implementations())

        # Detect features in events
        events = trait_ir.get("events", {})
        for event_name, event_nodes in events.items():
            node_features = _detect_features_in_nodes(event_nodes)
            if node_features['has_physics']:
                all_features['has_physics'] = True

    # Also collect global signals from autoloads (they may use signals from other classes)
    build_dir = arm.utils.build_dir()
    autoload_data = load_autoloads_json(build_dir)
    for autoload_name, autoload_ir in autoload_data.get("autoloads", {}).items():
        meta = autoload_ir.get("meta", {})
        for gs in meta.get("global_signals", []):
            global_signals.add(gs)

    # Generate global signal declarations with explicit zero initialization
    global_signal_decls = []
    global_signal_externs = []
    for gs in sorted(global_signals):
        global_signal_decls.append(f"ArmSignal {gs} = {{0}};")
        global_signal_externs.append(f"extern ArmSignal {gs};")

    template_data = {
        "trait_data_structs": "\n\n".join(trait_data_structs),
        "trait_declarations": "\n".join(trait_declarations),
        "event_handler_declarations": "\n".join(event_handler_declarations),
        "trait_implementations": "\n".join(trait_implementations),
        "global_signals": "\n".join(global_signal_decls),
        "global_signal_externs": "\n".join(global_signal_externs),
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
    lines = []
    lines.append(f'    {prefix}.trait_count = {len(traits)};')
    lines.append(f'    {prefix}.lifecycle_flags = 0;')

    if len(traits) > 0:
        lines.append(f'    {prefix}.traits = malloc(sizeof(ArmTrait) * {len(traits)});')

        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]

            # Get trait IR - must exist, macro provides all data
            trait_ir = n64_utils.get_trait(trait_info, trait_class)
            c_name = trait_ir.get("c_name", "")
            meta = trait_ir.get("meta", {})

            # Debug: log trait lookup
            if not c_name:
                print(f"[N64 codegen] WARNING: No c_name found for trait '{trait_class}'")
                print(f"[N64 codegen]   Available traits: {list(trait_info.get('traits', {}).keys())}")

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
        is_trigger = rb.get("is_trigger", False)
        use_deactivation = rb.get("use_deactivation", True)
        col_group = rb.get("collision_group", 1)
        col_mask = rb.get("collision_mask", 1)

        # Blender rigid body properties
        blender_type = rb.get("rb_type", "ACTIVE")  # 'PASSIVE' or 'ACTIVE'
        is_animated = rb.get("is_animated", False)   # Animated checkbox
        is_dynamic = rb.get("is_dynamic", True)      # Dynamic checkbox

        # Determine Oimo rigid body type:
        # Passive -> Static
        # Passive + Animated -> Kinematic
        # Active -> Kinematic
        # Active + Animated -> Kinematic
        # Active + Animated + Dynamic -> Kinematic
        # Active + Dynamic -> Dynamic
        if blender_type == "PASSIVE":
            if is_animated:
                rb_type = "OIMO_RIGID_BODY_KINEMATIC"
            else:
                rb_type = "OIMO_RIGID_BODY_STATIC"
        else:  # ACTIVE
            if is_dynamic and not is_animated:
                rb_type = "OIMO_RIGID_BODY_DYNAMIC"
            else:
                rb_type = "OIMO_RIGID_BODY_KINEMATIC"

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
        lines.append(f'        params.animated = {"true" if is_animated else "false"};')
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
            trait_ir = n64_utils.get_trait(trait_info, trait_class)
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
        trait_ir = n64_utils.get_trait(trait_info, trait_class)
        c_name = trait_ir.get("c_name", "")
        meta = trait_ir.get("meta", {})

        lines.append(f'    scene_traits[{i}].on_ready = {c_name}_on_ready;')
        lines.append(f'    scene_traits[{i}].on_fixed_update = {c_name}_on_fixed_update;')
        lines.append(f'    scene_traits[{i}].on_update = {c_name}_on_update;')
        lines.append(f'    scene_traits[{i}].on_late_update = {c_name}_on_late_update;')
        lines.append(f'    scene_traits[{i}].on_remove = {c_name}_on_remove;')

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


# =============================================================================
# Autoload JSON Loading and Code Generation
# =============================================================================

def load_autoloads_json(build_dir: str = None) -> dict:
    """
    Load the n64_autoloads.json file generated by the macro.

    Args:
        build_dir: Build directory path (defaults to arm.utils.build_dir())

    Returns:
        Parsed JSON dict with ir_version and autoloads
    """
    import arm.utils

    if build_dir is None:
        build_dir = arm.utils.build_dir()

    possible_paths = [
        os.path.join(build_dir, "n64_autoloads.json"),
        os.path.join(build_dir, "build", "n64_autoloads.json"),
        os.path.join(build_dir, "debug", "n64_autoloads.json"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    version = data.get("ir_version", 0)
                    if version != 1:
                        print(f"[N64] Warning: Expected autoload IR version 1, got {version}")
                    return data
            except Exception as e:
                print(f"[N64] Error loading {path}: {e}")

    return {"ir_version": 0, "autoloads": {}}


def _prepare_autoload_template_data(name: str, autoload_ir: dict) -> dict:
    """Prepare template data for a single autoload.

    Args:
        name: Autoload class name
        autoload_ir: IR dict from macro

    Returns:
        dict with all template placeholders
    """
    c_name = autoload_ir.get("c_name", name.lower())
    order = autoload_ir.get("order", 100)
    members = autoload_ir.get("members", [])
    functions = autoload_ir.get("functions", [])
    meta = autoload_ir.get("meta", {})
    signals = meta.get("signals", [])

    # Create emitter for code generation - use AutoloadIREmitter for proper prefixing
    member_names = [m["name"] for m in members]
    member_types = {m["name"]: m.get("ctype", "int32_t") for m in members}
    function_names = [f["name"] for f in functions]
    emitter = AutoloadIREmitter(name, c_name, member_names, function_names, member_types)

    # Helper to emit default value
    def emit_default_value(default: dict, ctype: str) -> str:
        if default is None:
            if ctype == "float":
                return "0.0f"
            elif ctype in ("int32_t", "int", "uint32_t", "uint8_t"):
                return "0"
            elif ctype == "bool":
                return "false"
            elif ctype == "const char*":
                return '""'
            elif ctype == "ArmSoundHandle":
                return "{-1, 0, -1, true}"  # channel=-1, mix_channel=0, sound_slot=-1, finished=true
            else:
                return "0"
        return emitter.emit(default)

    # Helper to generate function declaration
    def generate_function_declaration(func: dict) -> str:
        return_type = func.get("return_type", "void")
        func_c_name = func.get("c_name", f"{c_name}_{func.get('name', '')}")
        params = func.get("params", [])
        if params:
            param_str = ", ".join(f"{p.get('ctype', 'int32_t')} {p.get('name', '')}" for p in params)
        else:
            param_str = "void"
        return f"{return_type} {func_c_name}({param_str})"

    # Helper to generate function implementation
    def generate_function_implementation(func: dict, is_static: bool = False, maybe_unused: bool = False) -> str:
        decl = generate_function_declaration(func)
        prefix = ""
        if is_static:
            prefix = "static "
        if maybe_unused:
            prefix += "__attribute__((unused)) "
        lines = [f"{prefix}{decl} {{"]
        body = func.get("body", [])
        for node in body:
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

    # Build signal structs
    signal_struct_lines = []
    for sig in signals:
        struct_def = sig.get("struct_def")
        if struct_def:
            signal_struct_lines.append(struct_def)

    # Build member externs (for header)
    member_extern_lines = []
    if members:
        member_extern_lines.append(f"// {name} members")
        for m in members:
            ctype = m.get("ctype", "int32_t")
            mname = m.get("name", "")
            member_extern_lines.append(f"extern {ctype} {c_name}_{mname};")

    # Build signal externs (for header)
    signal_extern_lines = []
    if signals:
        signal_extern_lines.append(f"// {name} signals")
        for sig in signals:
            sig_name = sig.get("name", "")
            signal_extern_lines.append(f"extern ArmSignal {c_name}_{sig_name};")

    # Build function declarations (public only, for header)
    func_decl_lines = []
    public_funcs = [f for f in functions if f.get("is_public", False) and f.get("name") != "init"]
    if public_funcs:
        func_decl_lines.append(f"// {name} public functions")
        for func in public_funcs:
            decl = generate_function_declaration(func)
            func_decl_lines.append(f"{decl};")

    # Build member definitions (for source)
    member_def_lines = []
    if members:
        member_def_lines.append(f"// {name} members")
        for m in members:
            ctype = m.get("ctype", "int32_t")
            mname = m.get("name", "")
            default = m.get("default_value")
            init_value = emit_default_value(default, ctype)
            member_def_lines.append(f"{ctype} {c_name}_{mname} = {init_value};")

    # Build signal definitions (for source)
    signal_def_lines = []
    if signals:
        signal_def_lines.append(f"// {name} signals")
        for sig in signals:
            sig_name = sig.get("name", "")
            signal_def_lines.append(f"ArmSignal {c_name}_{sig_name} = {{0}};")

    # Build private function implementations
    private_func_lines = []
    private_funcs = [f for f in functions if not f.get("is_public", False) and f.get("name") != "init"]
    for func in private_funcs:
        # Mark as maybe_unused since setters might not be called externally
        impl = generate_function_implementation(func, is_static=True, maybe_unused=True)
        private_func_lines.append(impl)

    # Build signal handler wrappers
    # When a function is connected to a signal, we need a wrapper with the correct signature
    signal_handlers = meta.get("signal_handlers", [])
    signal_wrapper_lines = []
    for sh in signal_handlers:
        handler_name = sh.get("handler_name", "")
        if handler_name:
            # Find the function to get its parameters
            handler_func = next((f for f in functions if f["name"] == handler_name), None)
            params = handler_func.get("params", []) if handler_func else []

            # Generate wrapper that calls the actual function
            # Wrapper has ArmSignalHandler signature: void (*)(void* ctx, void* payload)
            wrapper_lines = [
                f"static void {c_name}_{handler_name}_wrapper(void* ctx, void* payload) {{",
                f"    (void)ctx;",
            ]

            if not params:
                # No parameters - just suppress payload warning and call
                wrapper_lines.append(f"    (void)payload;")
                wrapper_lines.append(f"    {c_name}_{handler_name}();")
            elif len(params) == 1:
                # Single parameter - check if signal provides this or if it's ignored
                # For signals like sceneLoaded that send const char*, cast payload
                p = params[0]
                ptype = p.get("ctype", "void*")
                if ptype == "const char*":
                    # If payload is NULL, pass empty string to avoid crash
                    wrapper_lines.append(f"    {c_name}_{handler_name}(payload ? (const char*)payload : \"\");")
                elif ptype in ("int32_t", "int"):
                    wrapper_lines.append(f"    {c_name}_{handler_name}((int32_t)(intptr_t)payload);")
                elif ptype == "float":
                    wrapper_lines.append(f"    {c_name}_{handler_name}(payload ? *(float*)payload : 0.0f);")
                else:
                    wrapper_lines.append(f"    {c_name}_{handler_name}(({ptype})payload);")
            else:
                # Multiple parameters - assume payload is a struct pointer
                wrapper_lines.append(f"    (void)payload;  // TODO: unpack struct")
                wrapper_lines.append(f"    // {c_name}_{handler_name}(...);")

            wrapper_lines.append(f"}}")
            signal_wrapper_lines.append("\n".join(wrapper_lines))

    # Build public function implementations
    public_func_lines = []
    for func in public_funcs:
        impl = generate_function_implementation(func, is_static=False)
        public_func_lines.append(impl)

    # Build init body
    init_body_lines = []
    init_func = next((f for f in functions if f.get("name") == "init"), None)
    if init_func:
        body = init_func.get("body", [])
        for node in body:
            code = emitter.emit(node)
            if code and code != "":
                for line in code.split('\n'):
                    if line.strip():
                        if not line.strip().endswith((';', '{', '}')):
                            init_body_lines.append(f"    {line};")
                        else:
                            init_body_lines.append(f"    {line}")

    return {
        'name': name,
        'c_name': c_name,
        'order': order,
        'signal_structs': '\n'.join(signal_struct_lines),
        'member_externs': '\n'.join(member_extern_lines),
        'signal_externs': '\n'.join(signal_extern_lines),
        'function_declarations': '\n'.join(func_decl_lines),
        'member_definitions': '\n'.join(member_def_lines),
        'signal_definitions': '\n'.join(signal_def_lines),
        'private_functions': '\n\n'.join(private_func_lines),
        'signal_wrappers': '\n\n'.join(signal_wrapper_lines),
        'public_functions': '\n\n'.join(public_func_lines),
        'init_body': '\n'.join(init_body_lines),
    }


def prepare_autoload_template_data():
    """Prepare template data for autoload file generation.

    Returns:
        tuple of (list of (c_name, template_data), master_data, features) or ([], None, {}) if no autoloads
        - list contains tuples of (c_name, template_data_dict) for each autoload
        - master_data is dict with 'includes' and 'init_calls' for autoloads.h
        - features is dict with 'has_audio', etc.
    """
    import arm.utils

    build_dir = arm.utils.build_dir()
    data = load_autoloads_json(build_dir)
    autoloads = data.get("autoloads", {})

    if not autoloads:
        return [], None, {}

    # Sort autoloads by order
    sorted_autoloads = sorted(autoloads.items(), key=lambda x: x[1].get("order", 100))
    autoload_data = []
    autoload_names = []
    all_global_signals = set()
    features = {'has_audio': False}

    for name, autoload_ir in sorted_autoloads:
        c_name = autoload_ir.get("c_name", name.lower())
        autoload_names.append(c_name)

        # Collect global signals from this autoload
        meta = autoload_ir.get("meta", {})
        for gs in meta.get("global_signals", []):
            all_global_signals.add(gs)

        # Detect audio usage in functions
        for func in autoload_ir.get("functions", []):
            if _detect_audio_in_nodes(func.get("body", [])):
                features['has_audio'] = True
                break

        # Prepare template data for this autoload
        tmpl_data = _prepare_autoload_template_data(name, autoload_ir)
        autoload_data.append((c_name, tmpl_data))

    # Prepare master autoloads.h data
    master_data = {
        'includes': '\n'.join(f'#include "{c_name}.h"' for c_name in autoload_names),
        'init_calls': '\n'.join(f'    {c_name}_init();' for c_name in autoload_names),
        'global_signals': list(all_global_signals),  # Pass to caller for merging with traits
    }

    return autoload_data, master_data, features


def _detect_audio_in_nodes(nodes: list) -> bool:
    """Recursively detect audio-related IR nodes."""
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = node.get("type", "")
        if node_type.startswith("audio_"):
            return True
        # Check children recursively
        if _detect_audio_in_nodes(node.get("children", [])):
            return True
        if _detect_audio_in_nodes(node.get("args", [])):
            return True
        if _detect_audio_in_nodes(node.get("body", [])):
            return True
    return False
