"""
Trait Emitter - Core IR→C translation engine for traits.

This module provides the TraitEmitter class which performs pure 1:1 translation
from IR nodes to C code. No semantic analysis - just translation.
"""

from typing import Dict, List, Optional


class TraitEmitter:
    """Emits C code from IR nodes. No semantic analysis, just translation."""

    def __init__(self, trait_name: str, c_name: str, member_names: List[str], is_trait: bool = True):
        self.trait_name = trait_name
        self.c_name = c_name
        self.member_names = member_names
        self.data_type = f"{trait_name}Data"
        self.is_trait = is_trait  # True for traits (use obj/data), False for autoloads (use NULL)

    def emit(self, node: Optional[Dict]) -> str:
        """Emit C code for an IR node."""
        if node is None:
            return ""

        node_type = node.get("type", "")
        method_name = f"emit_{node_type}"
        method = getattr(self, method_name, None)

        if method:
            return method(node)

        # Unknown node type - skip silently (may be intentional no-op)
        return ""

    def emit_list(self, nodes: List[Dict]) -> List[str]:
        """Emit list of nodes, filtering out empty results."""
        return [c for c in (self.emit(n) for n in nodes) if c]

    def emit_statements(self, nodes: List[Dict], indent: str = "    ") -> str:
        """Emit list of nodes as statements, adding semicolons where needed.

        Handles multi-line statements by indenting each line properly.
        """
        lines = self.emit_list(nodes)
        result = []
        for line in lines:
            # Add semicolon if line doesn't end with ; or } or is empty
            if line and not line.rstrip().endswith((';', '}', '{')):
                line = line + ';'
            # Handle multi-line statements by indenting each line
            for subline in line.split('\n'):
                result.append(f"{indent}{subline}")
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

    # =========================================================================
    # Lifecycle Control (removeUpdate, notifyOnUpdate at runtime)
    # =========================================================================

    def emit_remove_update(self, node: Dict) -> str:
        """removeUpdate() -> disable on_update callback via _update_enabled flag."""
        return f"(({self.data_type}*)data)->_update_enabled = false;"

    def emit_remove_late_update(self, node: Dict) -> str:
        """removeLateUpdate() -> disable on_late_update callback via _late_update_enabled flag."""
        return f"(({self.data_type}*)data)->_late_update_enabled = false;"

    def emit_remove_render2d(self, node: Dict) -> str:
        """removeRender2D() -> disable on_render2d callback via _render2d_enabled flag."""
        return f"(({self.data_type}*)data)->_render2d_enabled = false;"

    def emit_notify_update(self, node: Dict) -> str:
        """notifyOnUpdate() at runtime -> re-enable on_update callback."""
        return f"(({self.data_type}*)data)->_update_enabled = true;"

    def emit_notify_render2d(self, node: Dict) -> str:
        """notifyOnRender2D() at runtime -> re-enable on_render2d callback."""
        return f"(({self.data_type}*)data)->_render2d_enabled = true;"

    def emit_render2d_set_color(self, node: Dict) -> str:
        """g2.color = value -> assign color (already in RGBA32 format)."""
        args = node.get("args", [])
        if not args:
            return "_g2_color = RGBA32(0, 0, 0, 255);"
        color_val = self.emit(args[0])
        return f"_g2_color = {color_val};"

    def emit_render2d_fill_rect(self, node: Dict) -> str:
        """g2.fillRect(x, y, w, h) -> render2d_fill_rect(x, y, x+w, y+h, _g2_color)."""
        props = node.get("props", {})
        x = self.emit(props.get("x", {})) or "0"
        y = self.emit(props.get("y", {})) or "0"
        width = self.emit(props.get("width", {})) or "0"
        height = self.emit(props.get("height", {})) or "0"
        # N64 fill_rectangle takes x0, y0, x1, y1 (corners, not width/height)
        return f"render2d_fill_rect({x}, {y}, ({x}) + ({width}), ({y}) + ({height}), _g2_color);"

    def emit_color_from_floats(self, node: Dict) -> str:
        """Color.fromFloats(r, g, b, a) -> RGBA32 directly."""
        args = node.get("args", [])
        if len(args) >= 4:
            r = self.emit(args[0])
            g = self.emit(args[1])
            b = self.emit(args[2])
            a = self.emit(args[3])
            return f"RGBA32((uint8_t)(({r}) * 255.0f), (uint8_t)(({g}) * 255.0f), (uint8_t)(({b}) * 255.0f), (uint8_t)(({a}) * 255.0f))"
        return "RGBA32(0, 0, 0, 255)"

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
        """If statement.

        Unified IR format from both trait and autoload macros:
          children[0] = condition
          props.then = array of then body statement nodes
          props.else_ = array of else body statement nodes (optional, can be null)
        """
        children = node.get("children", [])
        props = node.get("props", {})

        if len(children) < 1:
            return ""

        cond = self.emit(children[0])
        if not cond:
            return ""

        then_nodes = props.get("then", [])
        if not then_nodes:
            return ""

        # Emit body with single indent level (caller adds outer indent via emit_statements)
        then_code = self.emit_statements(then_nodes, "    ")
        result = f"if ({cond}) {{\n{then_code}\n}}"

        # Check for else branch
        else_nodes = props.get("else_")
        if else_nodes:
            else_code = self.emit_statements(else_nodes, "    ")
            result += f" else {{\n{else_code}\n}}"

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
        """Function call - handles generic calls from macro.

        Trait macro uses 'method' field, autoload macro uses 'value' field.
        Support both for compatibility.
        """
        func_name = node.get("method", "") or node.get("value", "")
        if func_name:
            # IR uses 'args' for call arguments
            args = node.get("args", []) or node.get("children", [])
            arg_strs = [self.emit(a) for a in args if self.emit(a)]
            return f"{func_name}({', '.join(arg_strs)})"
        return ""

    def emit_method_call(self, node: Dict) -> str:
        """Method call on object: object.method(args).

        IR format:
            type: "method_call"
            method: "play"
            object: { type: "ident", value: "handle" }
            args: [...]

        For audio handles, maps to arm_audio_* functions.
        For tween methods (start, pause, stop) on tween_float/vec4/delay objects,
        we emit both the setup call and the tween control call.
        """
        method = node.get("method", "")
        obj_node = node.get("object")
        args = node.get("args", [])

        if not method or not obj_node:
            return ""

        obj_type = obj_node.get("type", "")

        # Handle tween method chaining: tween.float(...).start()
        # obj_node is tween_float/vec4/delay, method is start/pause/stop
        if obj_type in ("tween_float", "tween_vec4", "tween_delay"):
            # Get the actual tween variable from the nested tween node
            inner_tween = obj_node.get("object")
            tween_var = self.emit(inner_tween) if inner_tween else "NULL"

            # Collect capture assignments from callbacks
            capture_assignments = []
            props = obj_node.get("props", {})
            for cb_key in ("on_update", "on_done"):
                cb = props.get(cb_key)
                if cb:
                    captures = cb.get("captures", [])
                    for cap in captures:
                        if cap.get("is_param", False):
                            pname = cap.get("name", "")
                            # Emit assignment: capture_global = param
                            capture_assignments.append(f"{self.c_name}_capture_{pname} = {pname}")

            # Emit the setup call (tween_float, etc.)
            setup_call = self.emit(obj_node)

            # Emit the control call (tween_start, etc.)
            if method == "start":
                control_call = f"tween_start({tween_var})"
            elif method == "pause":
                control_call = f"tween_pause({tween_var})"
            elif method == "stop":
                control_call = f"tween_stop({tween_var})"
            else:
                control_call = ""

            # Return capture assignments, setup, and control as a sequence
            parts = capture_assignments + [setup_call]
            if control_call:
                parts.append(control_call)
            return ";\n    ".join(parts)

        obj = self.emit(obj_node)
        if not obj:
            return ""

        # Audio handle methods
        if method == "play":
            return f"arm_audio_start(&{obj})"
        elif method == "stop":
            return f"arm_audio_stop(&{obj})"
        elif method == "pause":
            return f"arm_audio_stop(&{obj})"  # No pause in libdragon
        elif method == "setVolume":
            vol = "1.0f"
            if args:
                vol = self.emit(args[0])
            return f"arm_audio_set_volume(&{obj}, {vol})"

        # Fallback: unknown method, emit as C function call
        arg_strs = [self.emit(a) for a in args]
        return f"{obj}.{method}({', '.join(arg_strs)})"

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

    def emit_new_vec(self, node: Dict) -> str:
        """Vec constructor with c_code template from macro."""
        c_code = node.get("c_code", "")
        if not c_code:
            return ""
        return self._substitute_placeholders(c_code, node.get("args", []))

    # =========================================================================
    # Audio Calls - emit audio nodes from AudioCallConverter
    # =========================================================================

    def emit_audio_load(self, node: Dict) -> str:
        """Audio load call - loads sound without playing it."""
        props = node.get("props", {})
        args = node.get("args", [])

        # Get sound path - either from args or c_code
        if args:
            sound_path = self.emit(args[0])
        else:
            c_code = node.get("c_code", "")
            if c_code:
                return c_code
            sound_path = '"rom:/sound.wav64"'

        mix_channel = props.get("mix_channel", "AUDIO_MIX_MASTER")
        loop = props.get("loop", "false")

        return f"arm_audio_load({sound_path}, {mix_channel}, {loop})"

    def emit_audio_play(self, node: Dict) -> str:
        """Audio play call - loads and immediately starts playing."""
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
        """Handle play - starts playback of a loaded handle."""
        children = node.get("children", [])
        if children:
            handle = self.emit(children[0])
            return f"arm_audio_start(&{handle})"
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

    # =========================================================================
    # Tween emit methods
    # =========================================================================

    def emit_tween_alloc(self, node: Dict) -> str:
        """Tween allocation from fixed pool."""
        return "tween_alloc()"

    def emit_tween_float(self, node: Dict) -> str:
        """Emit tween_float() call.

        The actual callback functions are generated separately at the autoload level.
        Here we just emit the setup and start calls.
        """
        obj = node.get("object")
        args = node.get("args", [])
        props = node.get("props", {})

        tween_var = self.emit(obj) if obj else "NULL"
        from_val = self.emit(args[0]) if args else "0.0f"
        to_val = self.emit(args[1]) if len(args) > 1 else "0.0f"
        duration = self.emit(args[2]) if len(args) > 2 else "1.0f"

        ease = props.get("ease", "EASE_LINEAR")
        on_update = props.get("on_update")
        on_done = props.get("on_done")

        # Get callback names
        update_cb = on_update.get("callback_name") if on_update else None
        done_cb = on_done.get("callback_name") if on_done else None

        update_str = f"{update_cb}_float" if update_cb else "NULL"
        done_str = f"{done_cb}_done" if done_cb else "NULL"

        # Tween returns itself for chaining, so emit setup
        # tween_float(tween, from, to, duration, on_update, on_done, ease, obj, data)
        # For traits, pass obj/data so callbacks can access trait members
        # For autoloads, pass NULL (callbacks access globals directly)
        obj_param = "obj" if self.is_trait else "NULL"
        data_param = "data" if self.is_trait else "NULL"
        return f"tween_float({tween_var}, {from_val}, {to_val}, {duration}, {update_str}, {done_str}, {ease}, {obj_param}, {data_param})"

    def emit_tween_vec4(self, node: Dict) -> str:
        """Emit tween_vec4() call."""
        obj = node.get("object")
        args = node.get("args", [])
        props = node.get("props", {})

        tween_var = self.emit(obj) if obj else "NULL"
        from_val = self.emit(args[0]) if args else "NULL"
        to_val = self.emit(args[1]) if len(args) > 1 else "NULL"
        duration = self.emit(args[2]) if len(args) > 2 else "1.0f"

        ease = props.get("ease", "EASE_LINEAR")
        on_update = props.get("on_update")
        on_done = props.get("on_done")

        update_cb = on_update.get("callback_name") if on_update else None
        done_cb = on_done.get("callback_name") if on_done else None

        update_str = f"{update_cb}_vec4" if update_cb else "NULL"
        done_str = f"{done_cb}_done" if done_cb else "NULL"

        obj_param = "obj" if self.is_trait else "NULL"
        data_param = "data" if self.is_trait else "NULL"
        return f"tween_vec4({tween_var}, &{from_val}, &{to_val}, {duration}, {update_str}, {done_str}, {ease}, {obj_param}, {data_param})"

    def emit_tween_delay(self, node: Dict) -> str:
        """Emit tween_delay() call."""
        obj = node.get("object")
        args = node.get("args", [])
        props = node.get("props", {})

        tween_var = self.emit(obj) if obj else "NULL"
        duration = self.emit(args[0]) if args else "1.0f"

        on_done = props.get("on_done")
        done_cb = on_done.get("callback_name") if on_done else None
        done_str = f"{done_cb}_done" if done_cb else "NULL"

        obj_param = "obj" if self.is_trait else "NULL"
        data_param = "data" if self.is_trait else "NULL"
        return f"tween_delay({tween_var}, {duration}, {done_str}, {obj_param}, {data_param})"

    def emit_tween_start(self, node: Dict) -> str:
        """Emit tween_start() call."""
        obj = node.get("object")
        tween_var = self.emit(obj) if obj else "NULL"
        return f"tween_start({tween_var})"

    def emit_tween_pause(self, node: Dict) -> str:
        """Emit tween_pause() call."""
        obj = node.get("object")
        tween_var = self.emit(obj) if obj else "NULL"
        return f"tween_pause({tween_var})"

    def emit_tween_stop(self, node: Dict) -> str:
        """Emit tween_stop() call."""
        obj = node.get("object")
        tween_var = self.emit(obj) if obj else "NULL"
        return f"tween_stop({tween_var})"
