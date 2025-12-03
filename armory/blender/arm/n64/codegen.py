"""
N64 Code Generator - Thin IR→C Emitter.

This module provides pure 1:1 IR→C mapping. All semantic analysis,
type resolution, coordinate swizzling, and event extraction happen
in the Haxe macro (N64TraitMacro.hx).

Pipeline:
  Haxe Macro (all semantics) → JSON IR → codegen.py (1:1 emit) → C code

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

IRNode types:
  Literals: int, float, string, bool, null
  Variables: member, ident, field
  Operators: assign, binop, unop
  Control: if, block
  Calls: call (with target: Scene, Transform, Math, Input)
  Constructors: new
"""

import json
import os
import math
from typing import Dict, List, Any, Optional

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
        """Emit list of nodes as statements."""
        lines = self.emit_list(nodes)
        return "\n".join(f"{indent}{line}" for line in lines)

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
                # Special case: transform.scale is an array, use it_set_scale()
                # Apply SCALE_FACTOR since Blender scale 1.0 != N64 scale 1.0
                # Coordinate conversion: Blender (x, y, z) → N64 (x, z, y) for scale
                if "->transform.scale" in target:
                    # Extract the object part (e.g., "((ArmObject*)obj)")
                    obj_part = target.replace("->transform.scale", "")
                    # value should be an ArmVec3 compound literal like (ArmVec3){x, y, z}
                    # Convert: Blender (x, y, z) → N64 (x, z, y) and multiply by SCALE_FACTOR
                    return f"it_set_scale(&{obj_part}->transform, ({value}).x * {SCALE_FACTOR}f, ({value}).z * {SCALE_FACTOR}f, ({value}).y * {SCALE_FACTOR}f);"
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
        """Block of statements."""
        children = node.get("children", [])
        return "\n".join(self.emit_list(children))

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

    # =========================================================================
    # Function Calls - All semantic decisions made by macro
    # =========================================================================

    def emit_call(self, node: Dict) -> str:
        """Generic function call - fallback for unknown calls."""
        method = node.get("method", "")
        args = node.get("args", [])
        obj_node = node.get("object")
        arg_strs = [self.emit(a) for a in args if self.emit(a)]

        # If there's an object, try to handle known method patterns
        if obj_node:
            obj = self.emit(obj_node)
            if obj:
                # Vec methods - delegate to vec_call handler
                vec_methods = {"mult", "add", "sub", "dot", "normalize", "length", "clone"}
                if method in vec_methods:
                    vec_node = {
                        "method": method,
                        "object": obj_node,
                        "args": args,
                        "props": {"vecType": "Vec2"}
                    }
                    result = self.emit_vec_call(vec_node)
                    if result:
                        return result

                # Physics methods
                physics_methods = {"applyForce", "applyImpulse", "setLinearVelocity", "getLinearVelocity"}
                if method in physics_methods:
                    physics_node = {
                        "method": method,
                        "object": obj_node,
                        "args": args
                    }
                    result = self.emit_physics_call(physics_node)
                    if result:
                        return result

        # Physics methods with no/skipped object - use self object
        physics_methods = {"applyForce", "applyImpulse", "setLinearVelocity", "getLinearVelocity"}
        if method in physics_methods:
            physics_node = {
                "method": method,
                "object": {"type": "ident", "value": "object"},
                "args": args
            }
            result = self.emit_physics_call(physics_node)
            if result:
                return result

        # Standard function call
        if method:
            return f"{method}({', '.join(arg_strs)})"
        return ""

    def emit_scene_call(self, node: Dict) -> str:
        """Scene.setActive() -> scene_switch_to()

        - String literal: macro provides c_code with SCENE_XXX enum (fast path)
        - Any other expression: use runtime helper scene_get_id_by_name()
        """
        # Fast path: macro resolved literal to enum
        if "c_code" in node:
            return node["c_code"] + ";"

        # Runtime path: use helper to map string -> SceneId
        args = node.get("args", [])
        if args:
            scene_expr = self.emit(args[0])
            return f"scene_switch_to(scene_get_id_by_name({scene_expr}));"
        return ""

    def emit_transform_call(self, node: Dict) -> str:
        """Transform calls with coordinate conversion Blender→N64."""
        method = node.get("method", "")
        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args if self.emit(a)]
        obj = "((ArmObject*)obj)"

        # Coordinate conversion: Blender XYZ → N64 XZ-Y
        if method == "translate" and len(arg_strs) >= 3:
            x, y, z = arg_strs[0], arg_strs[1], arg_strs[2]
            return f"it_translate(&{obj}->transform, {x}, {z}, -({y}));"

        if method == "rotate":
            # rotate(axis: Vec4, angle: Float) - axis is a Vec4, extract xyz components
            # Use global rotation (it_rotate_axis_global) for world-space rotation
            if len(arg_strs) >= 2:
                axis = arg_strs[0]  # Vec4 member like xRot
                angle = arg_strs[1]
                # Extract axis components and convert Blender→N64: (x,y,z) → (x,z,-y)
                ax = f"({axis}).x"
                ay = f"({axis}).y"
                az = f"({axis}).z"
                return f"it_rotate_axis_global(&{obj}->transform, {ax}, {az}, -({ay}), {angle});"
            elif len(arg_strs) >= 4:
                # Legacy: 4 separate args (ax, ay, az, angle)
                ax, ay, az, angle = arg_strs[0], arg_strs[1], arg_strs[2], arg_strs[3]
                return f"it_rotate_axis_global(&{obj}->transform, {ax}, {az}, -({ay}), {angle});"

        if method == "setLoc" and len(arg_strs) >= 3:
            x, y, z = arg_strs[0], arg_strs[1], arg_strs[2]
            return f"it_set_loc(&{obj}->transform, {x}, {z}, -({y}));"

        return ""

    def emit_math_call(self, node: Dict) -> str:
        """Math calls - function name already resolved by macro."""
        c_func = node.get("value", "")
        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args if self.emit(a)]
        return f"{c_func}({', '.join(arg_strs)})"

    def emit_input_call(self, node: Dict) -> str:
        """Input calls - macro provides ready-to-use C code."""
        return node.get("c_code", "0")

    def emit_physics_call(self, node: Dict) -> str:
        """Physics calls - resolved by macro."""
        method = node.get("method", "")
        obj_node = node.get("object")
        args = node.get("args", [])

        obj = self.emit(obj_node) if obj_node else ""
        # If object is empty (from skip node) or missing, use self object
        if not obj:
            obj = "((ArmObject*)obj)"
        arg_strs = [self.emit(a) for a in args if self.emit(a)]

        # Coordinate conversion: Blender (Z-up) → N64 (Y-up)
        # Blender (x, y, z) → N64 (x, z, -y)

        if method == "applyForce" and arg_strs:
            # physics_apply_force expects const OimoVec3* - pass address of compound literal
            vec_expr = arg_strs[0]
            return f"{{ OimoVec3 _force = (OimoVec3){{{vec_expr}.x, {vec_expr}.z, -({vec_expr}.y)}}; physics_apply_force({obj}->rigid_body, &_force); }}"

        if method == "applyImpulse" and arg_strs:
            vec_expr = arg_strs[0]
            return f"{{ OimoVec3 _impulse = (OimoVec3){{{vec_expr}.x, {vec_expr}.z, -({vec_expr}.y)}}; physics_apply_impulse({obj}->rigid_body, &_impulse); }}"

        if method == "setLinearVelocity" and arg_strs:
            vec_expr = arg_strs[0]
            return f"{{ OimoVec3 _vel = (OimoVec3){{{vec_expr}.x, {vec_expr}.z, -({vec_expr}.y)}}; physics_set_linear_velocity({obj}->rigid_body, &_vel); }}"

        if method == "getLinearVelocity":
            # Returns OimoVec3 (structurally identical to ArmVec3: {x, y, z})
            return f"physics_get_linear_velocity({obj}->rigid_body)"

        return ""

    def emit_vec_call(self, node: Dict) -> str:
        """Vec calls - type info from macro."""
        method = node.get("method", "")
        obj_node = node.get("object")
        args = node.get("args", [])
        props = node.get("props", {})
        vec_type = props.get("vecType", "Vec2")

        obj = self.emit(obj_node) if obj_node else ""
        if not obj:
            return ""

        arg_strs = [self.emit(a) for a in args if self.emit(a)]
        is_compound = obj.startswith("(Arm")
        v = f"({obj})" if is_compound else obj

        # Treat Vec4 as Vec3 for most operations (xyz components)
        is_vec3 = vec_type in ("Vec3", "Vec4")

        if method == "length":
            if is_vec3:
                return f"sqrtf({v}.x*{v}.x + {v}.y*{v}.y + {v}.z*{v}.z)"
            return f"sqrtf({v}.x*{v}.x + {v}.y*{v}.y)"

        if method == "mult" and arg_strs:
            s = arg_strs[0]
            if is_vec3:
                return f"(ArmVec3){{{v}.x*({s}), {v}.y*({s}), {v}.z*({s})}}"
            return f"(ArmVec2){{{v}.x*({s}), {v}.y*({s})}}"

        if method == "add" and arg_strs:
            o = f"({arg_strs[0]})" if arg_strs[0].startswith("(Arm") else arg_strs[0]
            if is_vec3:
                return f"(ArmVec3){{{v}.x+{o}.x, {v}.y+{o}.y, {v}.z+{o}.z}}"
            return f"(ArmVec2){{{v}.x+{o}.x, {v}.y+{o}.y}}"

        if method == "sub" and arg_strs:
            o = f"({arg_strs[0]})" if arg_strs[0].startswith("(Arm") else arg_strs[0]
            if is_vec3:
                return f"(ArmVec3){{{v}.x-{o}.x, {v}.y-{o}.y, {v}.z-{o}.z}}"
            return f"(ArmVec2){{{v}.x-{o}.x, {v}.y-{o}.y}}"

        if method == "dot" and arg_strs:
            o = f"({arg_strs[0]})" if arg_strs[0].startswith("(Arm") else arg_strs[0]
            if is_vec3:
                return f"({v}.x*{o}.x + {v}.y*{o}.y + {v}.z*{o}.z)"
            return f"({v}.x*{o}.x + {v}.y*{o}.y)"

        if method == "normalize":
            if is_compound:
                return ""  # cannot normalize compound literal inline
            if is_vec3:
                return f"{{ float _l=sqrtf({v}.x*{v}.x+{v}.y*{v}.y+{v}.z*{v}.z); if(_l>0.0f){{ {obj}.x/=_l; {obj}.y/=_l; {obj}.z/=_l; }} }}"
            return f"{{ float _l=sqrtf({v}.x*{v}.x+{v}.y*{v}.y); if(_l>0.0f){{ {obj}.x/=_l; {obj}.y/=_l; }} }}"

        # clone() just returns a copy of the vec
        if method == "clone":
            if is_vec3:
                return f"(ArmVec3){{{v}.x, {v}.y, {v}.z}}"
            return f"(ArmVec2){{{v}.x, {v}.y}}"

        return ""

    # =========================================================================
    # Constructors
    # =========================================================================

    def emit_new(self, node: Dict) -> str:
        """Constructor calls: new Vec3(x, y, z)"""
        type_name = node.get("value", "")
        args = node.get("args", [])
        arg_strs = [self.emit(a) for a in args]

        if type_name == "Vec4":
            # Vec4 treated as Vec3 (xyz components, ignore w)
            if len(arg_strs) >= 3:
                return f"(ArmVec3){{{arg_strs[0]}, {arg_strs[1]}, {arg_strs[2]}}}"
            return "(ArmVec3){0, 0, 0}"

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
    """Generates C code for a single trait from IR."""

    def __init__(self, name: str, ir: Dict, type_overrides: Dict = None):
        self.name = name
        self.c_name = ir.get("c_name", name.lower())
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
        """Generate the data struct for trait members."""
        if not self.members:
            return ""

        lines = [f"typedef struct {{"]
        for m in self.members:
            ctype = self._get_member_ctype(m)
            name = m.get("name", "unknown")
            lines.append(f"    {ctype} {name};")
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

        return "\n".join(impl_lines)


# =============================================================================
# Integration with Blender Export
# =============================================================================

def get_default_value_c(member: Dict) -> str:
    """Get C literal for member default value."""
    default = member.get("default_value")
    ctype = member.get("ctype", "float")

    if default is None:
        # Sensible defaults by type
        if ctype == "float":
            return "0.0f"
        if ctype in ("int32_t", "int"):
            return "0"
        if ctype == "bool":
            return "false"
        if ctype == "const char*":
            return "NULL"
        if ctype == "SceneId":
            return "SCENE_UNKNOWN"
        if "Vec" in ctype:
            return "{0}"
        return "0"

    # Use emitter to convert IR node to C
    emitter = IREmitter("", "", [])
    return emitter.emit(default) or "0"


def generate_trait_init(trait_name: str, members: List[Dict],
                        blender_overrides: Dict) -> str:
    """
    Generate trait initialization code.

    Args:
        trait_name: Name of the trait class
        members: List of member dicts from IR
        blender_overrides: Values from Blender scene export

    Returns:
        C initialization code
    """
    if not members:
        return f"    // {trait_name}: no data to initialize"

    data_type = f"{trait_name}Data"
    lines = [f"    {data_type}* data = ({data_type}*)trait_alloc(sizeof({data_type}));"]

    for m in members:
        name = m.get("name")
        ctype = m.get("ctype", "float")

        # Use Blender override if present, else default from macro
        if name in blender_overrides:
            value = format_blender_value(blender_overrides[name], ctype)
        else:
            value = get_default_value_c(m)

        lines.append(f"    data->{name} = {value};")

    return "\n".join(lines)


def format_blender_value(value: Any, ctype: str) -> str:
    """Format a Blender export value to C literal."""
    if value is None:
        return get_default_value_c({"ctype": ctype})

    if ctype == "float":
        return f"{float(value)}f"

    if ctype in ("int32_t", "int"):
        return str(int(value))

    if ctype == "bool":
        return "true" if value else "false"

    if ctype == "const char*":
        return f'"{value}"' if value else "NULL"

    if ctype == "SceneId":
        # Convert scene name to enum
        if isinstance(value, str):
            return f"SCENE_{value.upper().replace(' ', '_')}"
        return "SCENE_UNKNOWN"

    if "Vec3" in ctype and isinstance(value, (list, tuple)) and len(value) >= 3:
        return f"(ArmVec3){{{value[0]}f, {value[1]}f, {value[2]}f}}"

    if "Vec2" in ctype and isinstance(value, (list, tuple)) and len(value) >= 2:
        return f"(ArmVec2){{{value[0]}f, {value[1]}f}}"

    return str(value)


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
    """
    import arm.utils

    build_dir = arm.utils.build_dir()
    data = load_traits_json(build_dir)
    traits = data.get("traits", {})

    if not traits:
        print("[N64] No traits to generate")
        return

    data_dir = os.path.join(build_dir, "n64", "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    tmpl_dir = os.path.join(arm.utils.get_n64_deployment_path(), "src", "data")

    # Generate template substitution data
    template_data = _prepare_traits_template_data(traits, type_overrides)

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


def _prepare_traits_template_data(traits: dict, type_overrides: dict = None) -> dict:
    """Prepare data for traits.h.j2 and traits.c.j2 templates.

    Uses TraitCodeGenerator for each trait to avoid code duplication.
    """
    trait_data_structs = []
    trait_declarations = []
    event_handler_declarations = []
    trait_implementations = []

    for trait_name, trait_ir in traits.items():
        gen = TraitCodeGenerator(trait_name, trait_ir, type_overrides)

        # Header data: struct + declarations
        struct = gen.generate_data_struct()
        if struct:
            trait_data_structs.append(struct)

        trait_declarations.extend(gen.generate_lifecycle_declarations())
        event_handler_declarations.extend(gen.generate_button_event_declarations())

        # Implementation data
        trait_implementations.append(gen.generate_all_event_implementations())

    return {
        "trait_data_structs": "\n\n".join(trait_data_structs),
        "trait_declarations": "\n".join(trait_declarations),
        "event_handler_declarations": "\n".join(event_handler_declarations),
        "trait_implementations": "\n".join(trait_implementations),
    }


# =============================================================================
# Scene Generation - These combine Blender data with trait IR
# =============================================================================

def _fmt_vec3(v: List[float]) -> str:
    """Format a 3-element list as T3DVec3 initializer."""
    return f'(T3DVec3){{{{ {v[0]:.6f}f, {v[1]:.6f}f, {v[2]:.6f}f }}}}'


def generate_transform_block(prefix: str, pos: List[float],
                             rot: List[float] = None,
                             scale: List[float] = None) -> List[str]:
    """Generate C code for transform initialization."""
    lines = []
    # Position - already converted to N64 coords by caller
    lines.append(f'    {prefix}.transform.loc[0] = {pos[0]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[1] = {pos[1]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[2] = {pos[2]:.6f}f;')

    if rot:
        lines.append(f'    {prefix}.transform.rot[0] = {rot[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[1] = {rot[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[2] = {rot[2]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[3] = {rot[3]:.6f}f;')

    if scale:
        lines.append(f'    {prefix}.transform.scale[0] = {scale[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[1] = {scale[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[2] = {scale[2]:.6f}f;')
        lines.append(f'    {prefix}.transform.dirty = FB_COUNT;')

    return lines


def generate_trait_block(prefix: str, traits: List[Dict],
                         trait_info: dict, scene_name: str) -> List[str]:
    """Generate C code for trait initialization on an object."""
    from arm.n64 import utils as n64_utils
    import arm.utils

    lines = []
    lines.append(f'    {prefix}.trait_count = {len(traits)};')

    if len(traits) > 0:
        lines.append(f'    {prefix}.traits = malloc(sizeof(ArmTrait) * {len(traits)});')

        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]

            # Get trait IR for c_name and button events
            trait_ir = trait_info.get("traits", {}).get(trait_class, {})
            # Use c_name from IR (e.g., "arm_player_player") for function names
            c_name = trait_ir.get("c_name", arm.utils.safesrc(trait_class).lower())
            events = trait_ir.get("events", {})
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
        lines.extend(generate_transform_block(prefix, obj["pos"], obj["rot"], obj["scale"]))
        lines.append(f'    models_get({obj["mesh"]});')
        lines.append(f'    {prefix}.dpl = models_get_dpl({obj["mesh"]});')
        lines.append(f'    {prefix}.model_mat = malloc_uncached(sizeof(T3DMat4FP) * FB_COUNT);')
        lines.append(f'    {prefix}.visible = {str(obj["visible"]).lower()};')
        lines.append(f'    {prefix}.is_static = {str(obj.get("is_static", False)).lower()};')

        bc = obj.get("bounds_center", [0, 0, 0])
        br = obj.get("bounds_radius", 1.0)
        lines.append(f'    {prefix}.bounds_center = {_fmt_vec3(bc)};')
        lines.append(f'    {prefix}.bounds_radius = {br:.6f}f;')
        lines.append(f'    {prefix}.rigid_body = NULL;')

        lines.extend(generate_trait_block(prefix, obj.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_physics_block(objects: List[Dict], world_data: dict) -> str:
    """Generate C code for physics initialization."""
    lines = []

    gravity = world_data.get("gravity", [0, 0, -9.81])
    gx, gy, gz = gravity[0], gravity[1], gravity[2]
    # Convert Blender coords to N64: (X, Y, Z) → (X, Z, -Y)
    n64_gx, n64_gy, n64_gz = gx, gz, -gy
    lines.append(f'    physics_set_gravity({n64_gx:.6f}f, {n64_gy:.6f}f, {n64_gz:.6f}f);')
    lines.append('')

    for i, obj in enumerate(objects):
        rb = obj.get("rigid_body")
        if rb is None:
            continue

        prefix = f'objects[{i}]'
        mass = rb.get("mass", 1.0)
        friction = rb.get("friction", 0.5)
        restitution = rb.get("restitution", 0.0)
        is_kinematic = rb.get("is_kinematic", False)

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

        lines.append(f'    // Rigid body for {obj.get("name", f"object_{i}")}')

        if shape == "box":
            # Exporter provides half_extents directly
            half_extents = rb.get("half_extents", [0.5, 0.5, 0.5])
            hx, hy, hz = half_extents[0], half_extents[1], half_extents[2]
            lines.append(f'    physics_create_box(&{prefix}, {rb_type}, {hx:.6f}f, {hy:.6f}f, {hz:.6f}f, {mass:.6f}f, {friction:.6f}f, {restitution:.6f}f);')
        elif shape == "sphere":
            r = rb.get("radius", 0.5)
            lines.append(f'    physics_create_sphere(&{prefix}, {rb_type}, {r:.6f}f, {mass:.6f}f, {friction:.6f}f, {restitution:.6f}f);')
        elif shape == "capsule":
            r = rb.get("radius", 0.5)
            hh = rb.get("half_height", 0.5)
            lines.append(f'    physics_create_capsule(&{prefix}, {rb_type}, {r:.6f}f, {hh:.6f}f, {mass:.6f}f, {friction:.6f}f, {restitution:.6f}f);')
        else:
            # Default to box
            hx, hy, hz = 0.5, 0.5, 0.5
            lines.append(f'    physics_create_box(&{prefix}, {rb_type}, {hx:.6f}f, {hy:.6f}f, {hz:.6f}f, {mass:.6f}f, {friction:.6f}f, {restitution:.6f}f);')

        lines.append('')

    return '\n'.join(lines)


def generate_scene_traits_block(traits: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for scene-level traits."""
    if not traits:
        return "    // No scene-level traits"

    lines = []
    lines.append(f'    static ArmTrait scene_traits[{len(traits)}];')

    for i, trait in enumerate(traits):
        trait_class = trait["class_name"]
        import arm.utils

        # Get trait IR for c_name and button events
        trait_ir = trait_info.get("traits", {}).get(trait_class, {})
        # Use c_name from IR (e.g., "arm_level_level") for function names
        c_name = trait_ir.get("c_name", arm.utils.safesrc(trait_class).lower())
        events = trait_ir.get("events", {})
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


