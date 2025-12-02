"""
N64 Code Generator - Converts IR nodes to C code and fills templates.

This module handles:
1. IR emission (converting IR nodes from JSON to C code)
2. Template filling (generating traits.h, traits.c, scenes.c)
3. Scene data coordinate conversion

Pipeline: Haxe Macro → JSON (IR) → codegen.py → C code
"""

import json
import os
import math
from typing import Dict, List, Any, Optional

import arm.utils

from arm.n64.config import (
    BUTTON_MAP, INPUT_STATE_MAP, TYPE_MAP, MATH_FUNC_MAP, SKIP_MEMBERS,
    map_button, map_type, map_math_func,
    convert_vec3_list, convert_quat_list, convert_scale_list,
    convert_position_str, convert_scale_str, convert_direction_str,
    SCALE_FACTOR
)


# =============================================================================
# IR Emitter - Converts IR nodes to C code
# =============================================================================

class IREmitter:
    """Converts IR nodes to C code strings."""

    def __init__(self, trait_name: str, member_names: List[str]):
        self.trait_name = trait_name
        self.member_names = member_names
        self.skipped_locals = set()  # Track local vars that were skipped

    def emit(self, node: Dict) -> str:
        """Emit C code for an IR node."""
        if node is None:
            return ""

        node_type = node.get("type", "")
        emitter_method = getattr(self, f"emit_{node_type}", None)
        if emitter_method:
            return emitter_method(node)
        return ""

    def emit_statements(self, nodes: List[Dict]) -> str:
        """Emit multiple statements."""
        lines = []
        for node in nodes:
            code = self.emit(node)
            if code:
                lines.append(code)
        return "\n".join(lines)

    # === Literals ===

    def emit_IntLiteral(self, node: Dict) -> str:
        return str(node.get("value", 0))

    def emit_FloatLiteral(self, node: Dict) -> str:
        val = node.get("value", 0.0)
        # Ensure decimal point for valid C float literal
        s = str(val)
        if '.' not in s and 'e' not in s.lower():
            s = s + ".0"
        return f"{s}f"

    def emit_StringLiteral(self, node: Dict) -> str:
        val = node.get("value", "")
        if val is None or val == "None":
            return "NULL"
        return f'"{val}"'

    def emit_BoolLiteral(self, node: Dict) -> str:
        return "true" if node.get("value", False) else "false"

    def emit_NullLiteral(self, node: Dict) -> str:
        return "NULL"

    def emit_Identifier(self, node: Dict) -> str:
        """Handle bare identifiers - map known ones to C equivalents."""
        name = node.get("value", "")
        # Map Haxe identifiers to C
        identifier_map = {
            "None": "NULL",
            "null": "NULL",
            "true": "true",
            "false": "false",
        }
        return identifier_map.get(name, name)

    # === Variables ===

    def emit_MemberAccess(self, node: Dict) -> str:
        name = node.get("value", "")
        return f"(({self.trait_name}Data*)data)->{name}"

    def emit_LocalVar(self, node: Dict) -> str:
        name = node.get("value", "")
        # If it's a skipped API object or was skipped due to dependency
        if name in SKIP_MEMBERS or name in self.skipped_locals:
            return ""
        return name

    def emit_ParamRef(self, node: Dict) -> str:
        param = node.get("value", "")
        if param == "obj":
            return "((ArmObject*)obj)"
        elif param == "dt":
            return "dt"
        elif param == "data":
            return "data"
        return param

    # === Operators ===

    def emit_BinaryOp(self, node: Dict) -> str:
        op = node.get("value", "?")
        children = node.get("children", [])
        if len(children) >= 2:
            left = self.emit(children[0])
            right = self.emit(children[1])

            # If either operand is empty or a comment (skipped), return empty
            if not left or not right or left.startswith("/*") or left.startswith("//"):
                return ""
            if right.startswith("/*") or right.startswith("//"):
                return ""

            if op == "[]":
                return f"{left}[{right}]"
            return f"({left} {op} {right})"
        return ""

    def emit_UnaryOp(self, node: Dict) -> str:
        op = node.get("value", "?")
        children = node.get("children", [])
        props = node.get("props", {})
        postfix = props.get("postfix", False)
        if children:
            operand = self.emit(children[0])
            if not operand:
                return ""
            if postfix:
                return f"({operand}{op})"
            else:
                return f"({op}{operand})"
        return ""

    def emit_Assign(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 2:
            # Check if target is an API object that we skip
            target_node = children[0]
            var_name = None
            if target_node.get("type") == "LocalVar":
                var_name = target_node.get("value", "")
                if var_name in SKIP_MEMBERS:
                    self.skipped_locals.add(var_name)
                    return ""

            # Check for transform field assignment (scale, loc, rot are arrays)
            if target_node.get("type") == "TransformField":
                field = target_node.get("value", "")
                value_node = children[1]
                if field == "scale" and value_node.get("type") == "Vec3Create":
                    vec_children = value_node.get("children", [])
                    if len(vec_children) >= 3:
                        x = self.emit(vec_children[0])
                        y = self.emit(vec_children[1])
                        z = self.emit(vec_children[2])
                        if x and y and z:
                            return f"it_set_scale(&((ArmObject*)obj)->transform, {x}, {z}, {y});"
                    return ""

            target = self.emit(children[0])
            value = self.emit(children[1])

            # Skip if target or value is empty - mark local as skipped
            if not target or not value:
                if var_name:
                    self.skipped_locals.add(var_name)
                return ""

            # Handle transform array assignments - these are float[], can't assign struct
            if "transform.scale" in target or "transform.loc" in target or "transform.rot" in target:
                # Convert to it_set_* if value is a Vec3 initializer
                if "(ArmVec3){" in value:
                    # Extract components from (ArmVec3){x, y, z}
                    if "transform.scale" in target:
                        return ""  # Skip - should be handled by TransformField check above
                    elif "transform.loc" in target:
                        return ""
                    elif "transform.rot" in target:
                        return ""
                return ""

            return f"{target} = {value};"
        return ""

    def emit_AssignOp(self, node: Dict) -> str:
        op = node.get("value", "+=")
        children = node.get("children", [])
        if len(children) >= 2:
            target_node = children[0]
            value_node = children[1]

            # Check for transform property assignments (scale, loc, rot are arrays)
            if op == "=" and target_node.get("type") in ("GetScale", "GetPosition", "GetRotation"):
                # Handle Vec3Create assignments
                if value_node.get("type") == "Vec3Create":
                    vec_children = value_node.get("children", [])
                    if len(vec_children) >= 3:
                        x = self.emit(vec_children[0])
                        y = self.emit(vec_children[1])
                        z = self.emit(vec_children[2])
                        if x and y and z:
                            if target_node.get("type") == "GetScale":
                                return f"it_set_scale(&((ArmObject*)obj)->transform, {x}, {z}, {y});"
                            elif target_node.get("type") == "GetPosition":
                                return f"it_set_loc(&((ArmObject*)obj)->transform, {x}, {z}, -({y}));"
                            elif target_node.get("type") == "GetRotation":
                                return f"it_set_rot(&((ArmObject*)obj)->transform, {x}, {z}, -({y}), 1.0f);"
                # Skip other assignments to transform arrays
                return ""

            target = self.emit(children[0])
            value = self.emit(children[1])
            if not target or not value:
                return ""
            return f"{target} {op} {value};"
        return ""

    # === Control Flow ===

    def emit_IfStmt(self, node: Dict) -> str:
        children = node.get("children", [])
        props = node.get("props", {})
        if not children:
            return ""

        cond = self.emit(children[0])

        # If condition is empty, skip entire if
        if not cond or cond.strip() == "":
            return ""

        then_block = props.get("then", [])
        else_block = props.get("else_", [])
        then_code = self.emit_statements(then_block) if then_block else ""
        result = f"if ({cond}) {{ {then_code} }}"
        if else_block:
            else_code = self.emit_statements(else_block)
            result += f" else {{ {else_code} }}"
        return result

    def emit_WhileLoop(self, node: Dict) -> str:
        children = node.get("children", [])
        props = node.get("props", {})
        if not children:
            return ""

        cond = self.emit(children[0])
        body = props.get("body", [])
        body_code = self.emit_statements(body) if body else ""
        if props.get("doWhile", False):
            return f"do {{ {body_code} }} while ({cond});"
        else:
            return f"while ({cond}) {{ {body_code} }}"

    def emit_ForLoop(self, node: Dict) -> str:
        var_name = node.get("value", "i")
        children = node.get("children", [])
        props = node.get("props", {})
        if len(children) < 2:
            return ""

        start = self.emit(children[0])
        end = self.emit(children[1])
        body = props.get("body", [])
        body_code = self.emit_statements(body) if body else ""
        return f"for (int {var_name} = {start}; {var_name} < {end}; {var_name}++) {{ {body_code} }}"

    def emit_Block(self, node: Dict) -> str:
        children = node.get("children", [])
        return self.emit_statements(children)

    # === Transform Operations ===

    def emit_GetPosition(self, node: Dict) -> str:
        return "((ArmObject*)obj)->transform.loc"

    def emit_SetPosition(self, node: Dict) -> str:
        children = node.get("children", [])
        axis = node.get("value")

        if axis:
            value = self.emit(children[0]) if children else "0"
            if not value:
                return ""
            idx = {"x": 0, "y": 2, "z": 1}[axis]
            negate = axis == "y"
            if negate:
                return f"((ArmObject*)obj)->transform.loc[{idx}] = -({value}); ((ArmObject*)obj)->transform.dirty = FB_COUNT;"
            return f"((ArmObject*)obj)->transform.loc[{idx}] = {value}; ((ArmObject*)obj)->transform.dirty = FB_COUNT;"

        if len(children) >= 3:
            x = self.emit(children[0])
            y = self.emit(children[1])
            z = self.emit(children[2])
            if not x or not y or not z:
                return ""
            return f"it_set_loc(&((ArmObject*)obj)->transform, {x}, {z}, -({y}));"
        return ""

    def emit_GetRotation(self, node: Dict) -> str:
        return "((ArmObject*)obj)->transform.rot"

    def emit_SetRotation(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 4:
            x = self.emit(children[0])
            y = self.emit(children[1])
            z = self.emit(children[2])
            w = self.emit(children[3])
            if not x or not y or not z or not w:
                return ""
            return f"it_set_rot(&((ArmObject*)obj)->transform, {x}, {z}, -({y}), {w});"
        return ""

    def emit_GetScale(self, node: Dict) -> str:
        return "((ArmObject*)obj)->transform.scale"

    def emit_SetScale(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 3:
            x = self.emit(children[0])
            y = self.emit(children[1])
            z = self.emit(children[2])
            if not x or not y or not z:
                return ""
            return f"it_set_scale(&((ArmObject*)obj)->transform, {x}, {z}, {y});"
        return ""

    def emit_Translate(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 3:
            x = self.emit(children[0])
            y = self.emit(children[1])
            z = self.emit(children[2])
            if not x or not y or not z:
                return ""
            return f"it_translate(&((ArmObject*)obj)->transform, {x}, {z}, -({y}));"
        return ""

    def emit_Rotate(self, node: Dict) -> str:
        children = node.get("children", [])
        axis = node.get("value")

        if axis and len(children) >= 1:
            angle = self.emit(children[0])
            if not angle:
                return ""
            # Single axis rotation - use axis vector
            axis_vec = {"x": "1, 0, 0", "y": "0, 0, -1", "z": "0, 1, 0"}[axis]
            return f"it_rotate_axis(&((ArmObject*)obj)->transform, {axis_vec}, {angle});"

        if len(children) >= 4:
            ax = self.emit(children[0])
            ay = self.emit(children[1])
            az = self.emit(children[2])
            angle = self.emit(children[3])
            if not ax or not ay or not az or not angle:
                return ""
            return f"it_rotate_axis(&((ArmObject*)obj)->transform, {ax}, {az}, -({ay}), {angle});"
        return ""

    # === Input Operations ===

    def emit_ButtonDown(self, node: Dict) -> str:
        button = node.get("value", "a")
        n64_btn = map_button(button)
        return f"input_down({n64_btn})"

    def emit_ButtonStarted(self, node: Dict) -> str:
        button = node.get("value", "a")
        n64_btn = map_button(button)
        return f"input_started({n64_btn})"

    def emit_ButtonReleased(self, node: Dict) -> str:
        button = node.get("value", "a")
        n64_btn = map_button(button)
        return f"input_released({n64_btn})"

    def emit_StickX(self, node: Dict) -> str:
        return "input_stick_x()"

    def emit_StickY(self, node: Dict) -> str:
        return "input_stick_y()"

    # === Math Functions ===

    def emit_MathFunc(self, node: Dict) -> str:
        func = node.get("value", "")
        children = node.get("children", [])
        c_func = map_math_func(func)

        if func in ["PI", "POSITIVE_INFINITY", "NEGATIVE_INFINITY", "NaN"]:
            return c_func

        args = ", ".join(self.emit(c) for c in children)
        return f"{c_func}({args})"

    # === Vector Operations ===

    def emit_Vec3Create(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 3:
            x = self.emit(children[0])
            y = self.emit(children[1])
            z = self.emit(children[2])
            return f"(ArmVec3){{{x}, {z}, -({y})}}"
        return "(ArmVec3){0, 0, 0}"

    def emit_Vec3Component(self, node: Dict) -> str:
        component = node.get("value", "x")
        children = node.get("children", [])
        if children:
            vec = self.emit(children[0])
            idx = {"x": 0, "y": 2, "z": 1}[component]
            return f"({vec})[{idx}]"
        return "0"

    def emit_Vec3Length(self, node: Dict) -> str:
        children = node.get("children", [])
        if children:
            vec = self.emit(children[0])
            return f"vec3_length({vec})"
        return "0.0f"

    def emit_Vec3Normalize(self, node: Dict) -> str:
        children = node.get("children", [])
        if children:
            vec = self.emit(children[0])
            return f"vec3_normalize({vec})"
        return "(ArmVec3){0, 0, 0}"

    def emit_Vec3Dot(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 2:
            a = self.emit(children[0])
            b = self.emit(children[1])
            return f"vec3_dot({a}, {b})"
        return "0.0f"

    def emit_Vec3Add(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 2:
            a = self.emit(children[0])
            b = self.emit(children[1])
            return f"vec3_add({a}, {b})"
        return "(ArmVec3){0, 0, 0}"

    def emit_Vec3Sub(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 2:
            a = self.emit(children[0])
            b = self.emit(children[1])
            return f"vec3_sub({a}, {b})"
        return "(ArmVec3){0, 0, 0}"

    def emit_Vec3Mult(self, node: Dict) -> str:
        children = node.get("children", [])
        if len(children) >= 2:
            vec = self.emit(children[0])
            scalar = self.emit(children[1])
            return f"vec3_mult({vec}, {scalar})"
        return "(ArmVec3){0, 0, 0}"

    # === Scene Operations ===

    def emit_SetActiveScene(self, node: Dict) -> str:
        scene_name = node.get("value", "")
        scene_enum = f"SCENE_{scene_name.upper()}"
        return f"scene_set_pending({scene_enum});"

    # === Function Calls ===

    def emit_FunctionCall(self, node: Dict) -> str:
        func = node.get("value", "unknown")
        children = node.get("children", [])
        args = ", ".join(self.emit(c) for c in children)
        return f"{func}({args})"

    # === Generic/Fallback ===

    def emit_FieldAccess(self, node: Dict) -> str:
        field = node.get("value", "")
        children = node.get("children", [])
        if children:
            obj = self.emit(children[0])
            if not obj:
                return ""
            # Handle special known field accesses
            if obj == "Time" and field == "delta":
                return "dt"
            # Handle Vec3 struct field access (ArmVec3 has .x, .y, .z)
            if field in ("x", "y", "z"):
                # For ArmVec3 struct, use direct field access
                # But we need coordinate conversion for member variables
                # Map: Blender (x,y,z) -> N64 (x,z,-y)
                field_map = {"x": "x", "y": "z", "z": "y"}
                n64_field = field_map[field]
                if field == "y":
                    return f"(-({obj}).{n64_field})"
                return f"({obj}).{n64_field}"
            # Check if it's pointer access (cast expressions or pointers)
            if obj.startswith("((") and obj.endswith(")"):
                return f"{obj}->{field}"
            if obj.endswith(")"):
                return f"{obj}->{field}"
            return f"{obj}.{field}"
        return ""

    def emit_MethodCall(self, node: Dict) -> str:
        method = node.get("value", "")
        children = node.get("children", [])

        # Handle known vector methods
        if children:
            obj = self.emit(children[0])
            if not obj:
                return ""
            args = [self.emit(c) for c in children[1:]]

            # Vec3/Vec2 methods - map to libdragon fm_vec3_* functions
            # Note: These take pointers, but our ArmVec3 is a struct
            # For now, skip these - they need proper ArmVec3 math helpers
            if method == "length":
                # fm_vec3_len takes pointer, we have struct
                # Skip for now - code using this will be filtered
                return ""
            elif method == "normalize":
                return ""
            elif method == "dot" and args:
                return ""
            elif method == "cross" and args:
                return ""
            elif method == "mult" and args:
                return ""
            elif method == "add" and args:
                return ""
            elif method == "sub" and args:
                return ""

            # Unknown methods - return empty
            return ""
        return ""

    def emit_TransformField(self, node: Dict) -> str:
        field = node.get("value", "")
        return f"((ArmObject*)obj)->transform.{field}"

    def emit_TransformCall(self, node: Dict) -> str:
        method = node.get("value", "")
        children = node.get("children", [])
        # Filter out empty emissions
        arg_list = [self.emit(c) for c in children]
        arg_list = [a for a in arg_list if a and a.strip()]

        # Map method names to it_ functions
        method_map = {
            "translate": "it_translate",
            "rotate_axis": "it_rotate_axis",
            "rotate_axis_global": "it_rotate_axis_global",
            "set_loc": "it_set_loc",
            "set_rot": "it_set_rot",
            "set_scale": "it_set_scale",
            "buildMatrix": "",  # Not needed - handled by dirty flag
        }

        func_name = method_map.get(method, "")
        if not func_name:
            return ""  # Skip unknown or unneeded transform calls

        if arg_list:
            args = ", ".join(arg_list)
            return f"{func_name}(&((ArmObject*)obj)->transform, {args});"
        else:
            return f"{func_name}(&((ArmObject*)obj)->transform);"

    def emit_New(self, node: Dict) -> str:
        return ""


# =============================================================================
# High-Level IR Functions
# =============================================================================

def emit_ir_node(node: Dict, trait_name: str, member_names: List[str]) -> str:
    """Emit C code for a single IR node."""
    emitter = IREmitter(trait_name, member_names)
    return emitter.emit(node)


def emit_ir_statements(nodes: List[Dict], trait_name: str, member_names: List[str]) -> str:
    """Emit C code for a list of IR statement nodes."""
    emitter = IREmitter(trait_name, member_names)
    return emitter.emit_statements(nodes)


# =============================================================================
# Scene Data Conversion
# =============================================================================

def convert_scene_data(scene_data: dict) -> dict:
    """Apply coordinate conversion to all scene data (modifies in place)."""
    for scene_name, scene in scene_data.items():
        # Convert cameras
        for cam in scene.get('cameras', []):
            cam['pos'] = convert_vec3_list(cam['pos'])
            cam['target'] = convert_vec3_list(cam['target'])

        # Convert lights
        for light in scene.get('lights', []):
            light['dir'] = convert_vec3_list(light['dir'])
            # Normalize
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
# Template Loading
# =============================================================================

def get_template_dir() -> str:
    return os.path.join(arm.utils.get_n64_deployment_path(), "src", "data")


def load_template(name: str) -> str:
    path = os.path.join(get_template_dir(), name)
    with open(path, 'r') as f:
        return f.read()


# =============================================================================
# Trait JSON Loading
# =============================================================================

def load_traits_json(build_dir: str = None) -> dict:
    if build_dir is None:
        build_dir = arm.utils.build_dir()

    possible_paths = [
        os.path.join(build_dir, "n64_traits.json"),
        os.path.join(build_dir, "build", "n64_traits.json"),
        os.path.join(build_dir, "debug", "n64_traits.json"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)

    return {"version": 0, "traits": [], "summary": {}}


def get_trait_info(build_dir: str = None) -> dict:
    data = load_traits_json(build_dir)
    traits_dict = {}
    for trait in data.get("traits", []):
        traits_dict[trait["name"]] = trait

    return {
        "version": data.get("version", 0),
        "traits": traits_dict,
        "summary": data.get("summary", {})
    }


# =============================================================================
# Code Generation Helpers
# =============================================================================

def _is_valid_statement(stmt: str) -> bool:
    """Check if statement is valid C code."""
    if not stmt or not stmt.strip():
        return False
    if stmt.strip().startswith("if ()") or stmt.strip().startswith("if ( )"):
        return False
    if stmt.strip() in ["{}", "{ }", ";", ""]:
        return False
    return True


def _should_skip_trait(trait: dict) -> bool:
    """Check if trait should be skipped."""
    return trait.get("skip", False)


def _emit_ir_code(ir_nodes: list, trait_name: str, member_names: list) -> list:
    """Convert IR nodes to C code lines."""
    if not ir_nodes:
        return []
    code = emit_ir_statements(ir_nodes, trait_name, member_names)
    if code:
        return [line for line in code.split('\n') if line.strip()]
    return []


def _emit_ir_default_value(ir_node: dict) -> str:
    """Convert an IR node to a C default value string."""
    emitter = IREmitter("", [])
    return emitter.emit(ir_node)


# =============================================================================
# Trait Code Generation
# =============================================================================

def generate_trait_data_structs(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue
        if not trait.get("needs_data", False):
            continue

        name = trait["name"]
        members = trait.get("members", {})

        lines.append(f"// {name} trait data")
        lines.append(f"typedef struct {{")
        for member_name, member_info in members.items():
            # Map Haxe type to C type
            haxe_type = member_info.get('type', member_info.get('haxeType', 'float'))
            c_type = map_type(haxe_type)
            lines.append(f"    {c_type} {member_name};")
        lines.append(f"}} {name}Data;")
        lines.append("")

    return "\n".join(lines)


def generate_trait_data_externs(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue
        if not trait.get("needs_data", False):
            continue
        name = trait["name"]
        name_lower = name.lower()
        lines.append(f"extern {name}Data {name_lower}_data;")
    return "\n".join(lines)


def generate_trait_declarations(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue

        name = trait["name"]
        name_lower = name.lower()

        lines.append(f"// {name}")
        lines.append(f"void {name_lower}_on_ready(void* obj, void* data);")
        lines.append(f"void {name_lower}_on_fixed_update(void* obj, float dt, void* data);")
        lines.append(f"void {name_lower}_on_update(void* obj, float dt, void* data);")
        lines.append(f"void {name_lower}_on_remove(void* obj, void* data);")
        lines.append("")

    return "\n".join(lines)


def generate_trait_data_definitions(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue
        if not trait.get("needs_data", False):
            continue

        name = trait["name"]
        name_lower = name.lower()
        members = trait.get("members", {})

        init_parts = []
        for member_name, member_info in members.items():
            default = member_info.get("default_value", "0")
            haxe_type = member_info.get('type', member_info.get('haxeType', 'float'))

            if isinstance(default, dict):
                default = _emit_ir_default_value(default)
            elif default is None or default == "None" or str(default) == "None":
                default = "NULL"
            elif isinstance(default, (int, float)):
                # Ensure proper float literal format
                s = str(default)
                if '.' not in s and 'e' not in s.lower():
                    s = s + ".0"
                default = f"{s}f"
            elif isinstance(default, str):
                # Try to parse as number
                try:
                    num = float(default)
                    s = str(num)
                    if '.' not in s and 'e' not in s.lower():
                        s = s + ".0"
                    default = f"{s}f"
                except ValueError:
                    # It's a string literal or identifier
                    if default.startswith('"'):
                        pass  # Already quoted
                    elif haxe_type in ("String", "const char*"):
                        default = f'"{default}"'
            init_parts.append(f".{member_name} = {default}")

        init_str = " = {" + ", ".join(init_parts) + "}" if init_parts else " = {0}"
        lines.append(f"{name}Data {name_lower}_data{init_str};")

    return "\n".join(lines)


def generate_trait_implementations(traits: list) -> str:
    lines = []

    for trait in traits:
        if _should_skip_trait(trait):
            continue
        name = trait["name"]
        name_lower = name.lower()

        members = trait.get("members", {})
        member_names = list(members.keys())

        init_code = _emit_ir_code(trait.get("init", []), name, member_names)
        fixed_update_code = _emit_ir_code(trait.get("fixed_update", []), name, member_names)
        update_code = _emit_ir_code(trait.get("update", []), name, member_names)
        remove_code = _emit_ir_code(trait.get("remove", []), name, member_names)

        lines.append(f"// {name}")
        lines.append("")

        lines.append(f"void {name_lower}_on_ready(void* obj, void* data) {{")
        lines.append(f"    (void)obj; (void)data;")
        for stmt in init_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        lines.append(f"void {name_lower}_on_fixed_update(void* obj, float dt, void* data) {{")
        lines.append(f"    (void)obj; (void)data; (void)dt;")
        for stmt in fixed_update_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        lines.append(f"void {name_lower}_on_update(void* obj, float dt, void* data) {{")
        lines.append(f"    (void)obj; (void)data; (void)dt;")
        for stmt in update_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        lines.append(f"void {name_lower}_on_remove(void* obj, void* data) {{")
        lines.append(f"    (void)obj; (void)data;")
        for stmt in remove_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Event Code Generation
# =============================================================================

def collect_all_events(traits: list) -> dict:
    """Collect all unique event names across all traits, with their handlers."""
    all_events = {}
    for trait in traits:
        if _should_skip_trait(trait):
            continue
        events = trait.get("events", {})
        name = trait["name"]
        members = trait.get("members", {})
        member_names = list(members.keys())

        for event_name, code_data in events.items():
            if event_name not in all_events:
                all_events[event_name] = []
            all_events[event_name].append({
                "trait_name": name,
                "code": code_data,
                "member_names": member_names
            })
    return all_events


def generate_event_handler_declarations(traits: list) -> str:
    """Generate forward declarations for event handlers."""
    lines = []
    all_events = collect_all_events(traits)

    if not all_events:
        return "// No events defined"

    lines.append("// Event handler declarations")
    for event_name, handlers in all_events.items():
        for handler in handlers:
            trait_name = handler["trait_name"]
            func_name = f"{trait_name.lower()}_on_{event_name}"
            lines.append(f"void {func_name}(void* obj, void* data);")
    lines.append("")

    return "\n".join(lines)


def generate_event_handler_implementations(traits: list) -> str:
    """Generate event handler function bodies."""
    lines = []
    all_events = collect_all_events(traits)

    if not all_events:
        return "// No event handlers"

    lines.append("// Event handlers")
    for event_name, handlers in all_events.items():
        for handler in handlers:
            trait_name = handler["trait_name"]
            func_name = f"{trait_name.lower()}_on_{event_name}"
            member_names = handler.get("member_names", [])

            lines.append(f"void {func_name}(void* obj, void* data) {{")
            lines.append(f"    (void)obj; (void)data;")

            code = handler.get("code", [])
            if code and isinstance(code[0], dict):
                c_lines = _emit_ir_code(code, trait_name, member_names)
                for stmt in c_lines:
                    if _is_valid_statement(stmt):
                        lines.append(f"    {stmt}")
            lines.append("}")
            lines.append("")

    return "\n".join(lines)


def generate_event_subscription_arrays(traits: list) -> str:
    """Generate static arrays that map events to their handlers."""
    lines = []
    all_events = collect_all_events(traits)

    if not all_events:
        return "// No event subscriptions"

    lines.append("// Event subscription arrays")
    lines.append("typedef void (*EventHandler)(void* obj, void* data);")
    lines.append("")

    for event_name, handlers in all_events.items():
        array_name = f"event_{event_name}_handlers"
        count = len(handlers)

        func_names = [f"{h['trait_name'].lower()}_on_{event_name}" for h in handlers]
        lines.append(f"static const EventHandler {array_name}[{count}] = {{")
        for fn in func_names:
            lines.append(f"    {fn},")
        lines.append("};")
        lines.append(f"#define EVENT_{event_name.upper()}_COUNT {count}")
        lines.append("")

    lines.append("// Event dispatch")
    lines.append("static inline void dispatch_event(const char* event_name, void* obj, void* data) {")
    for event_name in all_events.keys():
        array_name = f"event_{event_name}_handlers"
        count_macro = f"EVENT_{event_name.upper()}_COUNT"
        lines.append(f'    if (strcmp(event_name, "{event_name}") == 0) {{')
        lines.append(f'        for (int i = 0; i < {count_macro}; i++) {{')
        lines.append(f'            {array_name}[i](obj, data);')
        lines.append(f'        }}')
        lines.append(f'        return;')
        lines.append(f'    }}')
    lines.append("}")
    lines.append("")

    # Button-specific dispatch functions
    button_events = {}
    for event_name, handlers in all_events.items():
        if event_name.startswith("btn_"):
            parts = event_name.split("_")
            if len(parts) >= 3:
                button = parts[1]
                method = parts[2]
                if button not in button_events:
                    button_events[button] = {}
                if method not in button_events[button]:
                    button_events[button][method] = []
                button_events[button][method].extend(handlers)

    if button_events:
        lines.append("// Button event dispatch functions")
        for button, methods in button_events.items():
            for method, handlers in methods.items():
                func_name = f"dispatch_btn_{button}_{method}"
                event_name = f"btn_{button}_{method}"
                array_name = f"event_{event_name}_handlers"
                count_macro = f"EVENT_{event_name.upper()}_COUNT"

                lines.append(f"static inline void {func_name}(void* obj, void* data) {{")
                lines.append(f"    for (int i = 0; i < {count_macro}; i++) {{")
                lines.append(f"        {array_name}[i](obj, data);")
                lines.append(f"    }}")
                lines.append("}")
                lines.append("")

    return "\n".join(lines)


# =============================================================================
# Template Filling
# =============================================================================

def fill_traits_h_template(traits: list) -> str:
    template = load_template("traits.h.j2")
    return template.format(
        trait_data_structs=generate_trait_data_structs(traits),
        trait_data_externs=generate_trait_data_externs(traits),
        trait_declarations=generate_trait_declarations(traits),
        event_handler_declarations=generate_event_handler_declarations(traits)
    )


def fill_traits_c_template(traits: list) -> str:
    template = load_template("traits.c.j2")
    return template.format(
        trait_data_definitions=generate_trait_data_definitions(traits),
        trait_implementations=generate_trait_implementations(traits),
        event_handler_implementations=generate_event_handler_implementations(traits),
        event_subscription_arrays=generate_event_subscription_arrays(traits)
    )


def write_traits_files():
    build_dir = arm.utils.build_dir()
    data = load_traits_json(build_dir)
    traits = data.get("traits", [])
    data_dir = os.path.join(build_dir, "n64", "src", "data")

    h_path = os.path.join(data_dir, "traits.h")
    with open(h_path, 'w') as f:
        f.write(fill_traits_h_template(traits))

    c_path = os.path.join(data_dir, "traits.c")
    with open(c_path, 'w') as f:
        f.write(fill_traits_c_template(traits))


# =============================================================================
# Scene Code Generation Helpers
# =============================================================================

def generate_transform_block(prefix: str, pos: list, rot: list = None, scale: list = None) -> list:
    """Generate C code for transform initialization."""
    lines = []
    lines.append(f'    {prefix}.transform.loc[0] = {pos[0]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[1] = {pos[1]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[2] = {pos[2]:.6f}f;')
    if rot is not None:
        lines.append(f'    {prefix}.transform.rot[0] = {rot[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[1] = {rot[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[2] = {rot[2]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[3] = {rot[3]:.6f}f;')
    if scale is not None:
        lines.append(f'    {prefix}.transform.scale[0] = {scale[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[1] = {scale[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[2] = {scale[2]:.6f}f;')
        lines.append(f'    {prefix}.transform.dirty = FB_COUNT;')
    return lines


def generate_trait_block(prefix: str, traits: list, trait_info: dict, scene_name: str) -> list:
    """Generate C code for trait initialization."""
    from arm.n64 import utils as n64_utils

    lines = []
    lines.append(f'    {prefix}.trait_count = {len(traits)};')
    if len(traits) > 0:
        lines.append(f'    {prefix}.traits = malloc(sizeof(ArmTrait) * {len(traits)});')
        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]
            trait_func_name = arm.utils.safesrc(trait_class).lower()
            lines.append(f'    {prefix}.traits[{t_idx}].on_ready = {trait_func_name}_on_ready;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_fixed_update = {trait_func_name}_on_fixed_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_update = {trait_func_name}_on_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_remove = {trait_func_name}_on_remove;')

            if n64_utils.trait_needs_data(trait_info, trait_class):
                struct_name = f'{trait_class}Data'
                instance_props = trait.get("props", {})
                initializer = n64_utils.build_trait_initializer(trait_info, trait_class, scene_name, instance_props)
                lines.append(f'    {prefix}.traits[{t_idx}].data = malloc(sizeof({struct_name}));')
                lines.append(f'    *({struct_name}*){prefix}.traits[{t_idx}].data = ({struct_name}){{{initializer}}};')
            else:
                lines.append(f'    {prefix}.traits[{t_idx}].data = NULL;')
    else:
        lines.append(f'    {prefix}.traits = NULL;')
    return lines


def _fmt_vec3(v: list) -> str:
    """Format a 3-element list as T3DVec3 initializer."""
    return f'(T3DVec3){{{{ {v[0]:.6f}f, {v[1]:.6f}f, {v[2]:.6f}f }}}}'


def generate_camera_block(cameras: list, trait_info: dict, scene_name: str) -> str:
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


def generate_light_block(lights: list, trait_info: dict, scene_name: str) -> str:
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


def generate_object_block(objects: list, trait_info: dict, scene_name: str) -> str:
    """Generate C code for all objects in a scene."""
    lines = []
    for i, obj in enumerate(objects):
        prefix = f'objects[{i}]'
        lines.extend(generate_transform_block(prefix, obj["pos"], obj["rot"], obj["scale"]))
        lines.append(f'    models_get({obj["mesh"]});')
        lines.append(f'    {prefix}.dpl = models_get_dpl({obj["mesh"]});')
        lines.append(f'    {prefix}.model_mat = malloc_uncached(sizeof(T3DMat4FP) * FB_COUNT);')
        lines.append(f'    {prefix}.visible = {str(obj["visible"]).lower()};')
        bc = obj.get("bounds_center", [0, 0, 0])
        br = obj.get("bounds_radius", 1.0)
        lines.append(f'    {prefix}.bounds_center = {_fmt_vec3(bc)};')
        lines.append(f'    {prefix}.bounds_radius = {br:.6f}f;')
        lines.append(f'    {prefix}.rigid_body = NULL;')
        lines.extend(generate_trait_block(prefix, obj.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_physics_block(objects: list, world_data: dict) -> str:
    """Generate C code for physics initialization."""
    lines = []

    gravity = world_data.get("gravity", [0, 0, -9.81])
    gx, gy, gz = gravity[0], gravity[1], gravity[2]
    n64_gx, n64_gy, n64_gz = gx, gz, -gy
    lines.append(f'    physics_set_gravity({n64_gx:.6f}f, {n64_gy:.6f}f, {n64_gz:.6f}f);')
    lines.append('')

    for i, obj in enumerate(objects):
        rb = obj.get("rigid_body")
        if rb is None:
            continue

        obj_name = obj.get("name", f"object_{i}")
        shape = rb.get("shape", "box")
        mass = rb.get("mass", 0.0)
        friction = rb.get("friction", 0.5)
        restitution = rb.get("restitution", 0.0)
        col_group = rb.get("collision_group", 1)
        col_mask = rb.get("collision_mask", 1)
        is_kinematic = rb.get("is_kinematic", False)

        if mass == 0.0:
            body_type = "OIMO_BODY_STATIC"
        elif is_kinematic:
            body_type = "OIMO_BODY_KINEMATIC"
        else:
            body_type = "OIMO_BODY_DYNAMIC"

        lines.append(f'    // Physics body for {obj_name}')
        lines.append('    {')
        lines.append(f'        OimoRigidBodyConfig rb_config = oimo_rigidbody_config_default();')
        lines.append(f'        rb_config.type = {body_type};')
        lines.append(f'        rb_config.position = oimo_vec3(objects[{i}].transform.loc[0], objects[{i}].transform.loc[1], objects[{i}].transform.loc[2]);')
        lines.append(f'        OimoQuat init_rot = oimo_quat(objects[{i}].transform.rot[0], objects[{i}].transform.rot[1], objects[{i}].transform.rot[2], objects[{i}].transform.rot[3]);')
        lines.append(f'        rb_config.rotation = oimo_quat_to_mat3(&init_rot);')
        lines.append(f'        OimoShapeConfig shape_config = oimo_shape_config_default();')
        lines.append(f'        shape_config.friction = {friction:.6f}f;')
        lines.append(f'        shape_config.restitution = {restitution:.6f}f;')
        lines.append(f'        shape_config.collision_group = {col_group};')
        lines.append(f'        shape_config.collision_mask = {col_mask};')

        if shape == "sphere":
            radius = rb.get("radius", 1.0)
            volume = (4.0 / 3.0) * 3.14159265 * radius ** 3
            density = 0.0 if mass == 0.0 else mass / volume
            lines.append(f'        shape_config.density = {density:.6f}f;')
            lines.append(f'        shape_config.geometry = oimo_geometry_sphere({radius:.6f}f);')
        elif shape == "capsule":
            radius = rb.get("radius", 0.5)
            half_height = rb.get("half_height", 0.5)
            volume = 3.14159265 * radius * radius * (2.0 * half_height) + (4.0 / 3.0) * 3.14159265 * radius ** 3
            density = 0.0 if mass == 0.0 else mass / volume
            lines.append(f'        shape_config.density = {density:.6f}f;')
            lines.append(f'        shape_config.geometry = oimo_geometry_capsule({radius:.6f}f, {half_height:.6f}f);')
        else:
            he = rb.get("half_extents", [1, 1, 1])
            volume = 8.0 * he[0] * he[1] * he[2]
            density = 0.0 if mass == 0.0 else mass / volume
            lines.append(f'        shape_config.density = {density:.6f}f;')
            lines.append(f'        shape_config.geometry = oimo_geometry_box({he[0]:.6f}f, {he[1]:.6f}f, {he[2]:.6f}f);')

        lines.append(f'        OimoRigidBody* body = (OimoRigidBody*)malloc(sizeof(OimoRigidBody));')
        lines.append(f'        oimo_rigidbody_init(body, &rb_config);')
        lines.append(f'        OimoShape* shape = (OimoShape*)malloc(sizeof(OimoShape));')
        lines.append(f'        oimo_shape_init(shape, &shape_config);')
        lines.append(f'        oimo_rigidbody_add_shape(body, shape);')

        if body_type == "OIMO_BODY_DYNAMIC":
            angular_friction = 0.1
            lines.append(f'        body->_mass = {mass:.6f}f;')
            lines.append(f'        body->_localInertia = oimo_mat3({angular_friction}f, 0, 0, 0, {angular_friction}f, 0, 0, 0, {angular_friction}f);')
            lines.append(f'        oimo_rigid_body_complete_mass_data(body);')

        lines.append('        oimo_world_add_rigidbody(physics_get_world(), body);')
        lines.append(f'        objects[{i}].rigid_body = body;')
        lines.append('    }')
        lines.append('')

    return '\n'.join(lines)


def generate_scene_traits_block(traits: list, trait_info: dict, scene_name: str) -> str:
    """Generate C code for scene-level traits."""
    lines = generate_trait_block('(*scene)', traits, trait_info, scene_name)
    return '\n'.join(lines)
