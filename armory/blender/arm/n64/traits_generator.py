"""
N64 Traits Code Generator

Generates N64 C code for libdragon/Tiny3D from Haxe trait metadata.
Uses Jinja2-style templates located in armorcore/Deployment/n64/src/data/.

The metadata is extracted at compile-time by the N64TraitMacro build macro
and written to n64_traits.json in the build directory.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import re
import json
import os

# Try to import arm module (available when running inside Blender)
try:
    import arm
    import arm.utils
    import arm.log as log
    from arm.n64.config import get_config
    from arm.n64 import utils as n64_utils
    HAS_ARM = True
except ImportError:
    HAS_ARM = False
    class LogStub:
        @staticmethod
        def warn(msg): print(f'WARN: {msg}')
        @staticmethod
        def info(msg): print(f'INFO: {msg}')
    log = LogStub()
    from config import get_config
    import utils as n64_utils

if HAS_ARM:
    if arm.is_reload(__name__):
        arm.utils = arm.reload_module(arm.utils)
        log = arm.reload_module(log)
        n64_utils = arm.reload_module(n64_utils)
    else:
        arm.enable_reload(__name__)


def safesrc(name: str) -> str:
    """Make a string safe for use as a C identifier."""
    if HAS_ARM:
        return arm.utils.safesrc(name)
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


# =============================================================================
# Template Loading
# =============================================================================

def get_template_dir() -> str:
    """Get the path to the template directory."""
    if HAS_ARM:
        sdk_path = arm.utils.get_sdk_path()
        return os.path.join(sdk_path, 'armorcore', 'Deployment', 'n64', 'src', 'data')
    return './armorcore/Deployment/n64/src/data'


def load_template(name: str) -> str:
    """Load a template file."""
    path = os.path.join(get_template_dir(), name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    log.warn(f'Template not found: {path}')
    return ''


def apply_template(template: str, **kwargs) -> str:
    """Apply simple {placeholder} substitutions to a template.

    Also handles Jinja2-style {{ and }} escapes, converting them to single braces.
    """
    result = template
    for key, value in kwargs.items():
        result = result.replace('{' + key + '}', str(value))
    # Handle Jinja2-style escaped braces
    result = result.replace('{{', '{')
    result = result.replace('}}', '}')
    return result


# =============================================================================
# Code Generation Context
# =============================================================================

@dataclass
class GeneratorContext:
    """Context passed during code generation."""
    trait_name: str
    func_name: str
    member_names: Set[str] = None
    local_vars: Set[str] = None  # Track local variable names declared in current scope
    vec4_vars: Set[str] = None   # Track Vec4 local variable names
    indent: int = 1
    needs_obj: bool = False
    needs_data: bool = False
    has_dt: bool = False

    def __post_init__(self):
        if self.member_names is None:
            self.member_names = set()
        if self.local_vars is None:
            self.local_vars = set()
        if self.vec4_vars is None:
            self.vec4_vars = set()

    def indent_str(self) -> str:
        return '    ' * self.indent


# =============================================================================
# Expression Generator
# =============================================================================

class ExpressionGenerator:
    """Generates C code from JSON expression nodes."""

    def __init__(self, ctx: GeneratorContext):
        self.ctx = ctx

    def generate(self, node: Dict) -> str:
        """Generate C code for an expression node."""
        if node is None:
            return '/* null */'

        node_type = node.get('type')

        if node_type == 'int':
            return str(node.get('value', 0))
        elif node_type == 'float':
            val = float(node.get('value', 0.0))
            # Ensure proper float formatting (e.g., 0.0f not 0f)
            if val == int(val):
                return f'{int(val)}.0f'
            return f'{val}f'
        elif node_type == 'string':
            return f'"{node.get("value", "")}"'
        elif node_type == 'ident':
            return self._gen_ident(node)
        elif node_type == 'field':
            return self._gen_field(node)
        elif node_type == 'binop':
            return self._gen_binop(node)
        elif node_type == 'unop':
            return self._gen_unop(node)
        elif node_type == 'call':
            return self._gen_call(node)
        elif node_type == 'new':
            return self._gen_new(node)
        else:
            log.warn(f'Unknown expression type: {node_type}')
            return f'/* unknown: {node_type} */'

    def _gen_ident(self, node: Dict) -> str:
        name = node.get('name', '')
        if name == 'true':
            return 'true'
        elif name == 'false':
            return 'false'
        elif name == 'this':
            return 'self'
        elif name == 'gamepad':
            return '/* no-op */'
        elif name in self.ctx.member_names:
            self.ctx.needs_data = True
            return f'tdata->{name}'
        return name

    def _gen_field(self, node: Dict) -> str:
        obj = node.get('object')
        field = node.get('field', '')

        # Handle Time.delta
        if obj and obj.get('type') == 'ident' and obj.get('name') == 'Time':
            if field == 'delta':
                self.ctx.has_dt = True
                return 'dt'
            return f'/* Time.{field} */'

        # Handle gamepad.leftStick.x/y -> input_stick_x()/input_stick_y()
        if obj and obj.get('type') == 'field':
            parent_obj = obj.get('object')
            parent_field = obj.get('field', '')
            if parent_obj and parent_obj.get('type') == 'ident':
                parent_name = parent_obj.get('name', '')
                # gamepad.leftStick.x or gamepad.leftStick.y
                if parent_name == 'gamepad' and parent_field == 'leftStick':
                    if field == 'x':
                        return 'input_stick_x()'
                    elif field == 'y':
                        return 'input_stick_y()'
                # Also handle rightStick if needed in the future
                elif parent_name == 'gamepad' and parent_field == 'rightStick':
                    if field == 'x':
                        return 'input_stick_x()'  # N64 only has one stick
                    elif field == 'y':
                        return 'input_stick_y()'

        # Handle gamepad access that isn't stick (skip it)
        if obj and obj.get('type') == 'ident' and obj.get('name') == 'gamepad':
            # Direct gamepad field access like gamepad.leftStick - return placeholder
            # This will be handled by parent field access
            return f'/* gamepad.{field} */'

        # Handle object.transform etc
        if obj and obj.get('type') == 'ident' and obj.get('name') == 'object':
            self.ctx.needs_obj = True
            return f'obj->{field}'

        # Handle this.member
        if obj and obj.get('type') == 'ident' and obj.get('name') in ('this', 'self'):
            self.ctx.needs_data = True
            return f'tdata->{field}'

        # Check if field is a trait member
        if field in self.ctx.member_names:
            self.ctx.needs_data = True
            return f'tdata->{field}'

        # Default: generate parent.field
        parent = self.generate(obj) if obj else ''
        # Skip generating field access if parent is a comment/no-op
        if parent.startswith('/*'):
            return f'/* {parent}.{field} */'
        return f'{parent}.{field}' if parent else field

    def _gen_binop(self, node: Dict) -> str:
        left = self.generate(node.get('left'))
        right = self.generate(node.get('right'))
        op = node.get('op', '?')
        return f'({left} {op} {right})'

    def _gen_unop(self, node: Dict) -> str:
        """Generate C code for unary operators like !, -, ~"""
        op = node.get('op', '')
        expr = self.generate(node.get('expr'))
        if op == '!':
            return f'!{expr}'
        elif op == '-':
            return f'-{expr}'
        elif op == '~':
            return f'~{expr}'
        else:
            return f'{op}{expr}'

    def _gen_call(self, node: Dict) -> str:
        path = node.get('path', '')
        args = node.get('args') or []

        # Parse path to get target.method
        parts = path.split('.')
        if len(parts) >= 2:
            target = parts[-2].lower()
            method = parts[-1].lower()
        else:
            target = ''
            method = parts[0].lower() if parts else ''

        # Handle special cases
        if target == 'input' and method == 'getgamepad':
            return '/* no-op */'

        # Look up in codegen config
        config = get_config()
        api_def = config.get_codegen_api(target, method)

        if api_def:
            return self._apply_api_template(api_def, args)

        log.warn(f'Unknown call: {path}')
        return f'/* unknown: {path} */'

    def _apply_api_template(self, api_def, args: List[Dict]) -> str:
        """Apply a codegen API template."""
        # Set context flags
        if api_def.flags.get('needs_obj'):
            self.ctx.needs_obj = True
        if api_def.flags.get('needs_data'):
            self.ctx.needs_data = True
        if api_def.flags.get('has_dt'):
            self.ctx.has_dt = True

        output = api_def.output

        # Check for variants
        if api_def.variants:
            # Member access variant for scene calls
            if 'member_access' in api_def.variants and args:
                arg = args[0]
                if arg and arg.get('type') == 'ident':
                    name = arg.get('name', '')
                    if name in self.ctx.member_names or name in ('nextLevel', 'targetScene'):
                        output = api_def.variants['member_access']
                        self.ctx.needs_data = True

            # Argument count variants
            variant_key = f'{len(args)}_arg'
            if variant_key in api_def.variants:
                output = api_def.variants[variant_key]

        # Build substitutions
        subs = self._build_subs(api_def, args)

        # Apply substitutions
        for key, value in subs.items():
            output = output.replace(f'{{{key}}}', value)

        return output

    def _build_subs(self, api_def, args: List[Dict]) -> Dict[str, str]:
        """Build template substitutions from arguments."""
        subs = {}
        args_spec = api_def.args or []
        config = get_config()

        for i, arg in enumerate(args or []):
            if arg is None:
                continue

            # Get arg name from spec or use positional
            arg_name = args_spec[i] if i < len(args_spec) else f'arg{i}'
            arg_type = arg.get('type')

            if arg_type == 'string':
                value = arg.get('value', '')
                if arg_name == 'button':
                    subs[arg_name] = config.get_n64_button(value)
                elif arg_name == 'scene':
                    subs[arg_name] = value
                    subs['scene_id'] = f'SCENE_{safesrc(value).upper()}'
                else:
                    subs[arg_name] = value
            elif arg_type == 'new' and arg.get('typeName') == 'Vec4':
                vec_args = arg.get('args') or []
                if len(vec_args) >= 3:
                    # Extract Vec4 components
                    x_val = self._get_const_value(vec_args[0])
                    y_val = self._get_const_value(vec_args[1])
                    z_val = self._get_const_value(vec_args[2])

                    subs['x'] = self.generate(vec_args[0])
                    subs['y'] = self.generate(vec_args[1])
                    subs['z'] = self.generate(vec_args[2])

                    # For rotation: compute axis index at compile-time
                    # Uses centralized Blender Z-up to N64 Y-up coordinate conversion
                    if x_val is not None and y_val is not None and z_val is not None:
                        # Determine dominant axis and use centralized mapping
                        axis_map = n64_utils.N64_AXIS_ROTATION_MAP

                        if abs(z_val) > abs(x_val) and abs(z_val) > abs(y_val):
                            # Blender Z axis
                            idx, negate = axis_map['z']
                            subs['axis_index'] = str(idx)
                            subs['angle_sign'] = '-' if (z_val > 0) == negate else ''
                        elif abs(y_val) > abs(x_val) and abs(y_val) > abs(z_val):
                            # Blender Y axis
                            idx, negate = axis_map['y']
                            subs['axis_index'] = str(idx)
                            subs['angle_sign'] = '-' if (y_val > 0) == negate else ''
                        elif abs(x_val) > abs(y_val) and abs(x_val) > abs(z_val):
                            # Blender X axis
                            idx, negate = axis_map['x']
                            subs['axis_index'] = str(idx)
                            subs['angle_sign'] = '-' if (x_val > 0) == negate else ''
                        else:
                            # Default to Blender Z (N64 Y up) if can't determine
                            idx, negate = axis_map['z']
                            subs['axis_index'] = str(idx)
                            subs['angle_sign'] = '-' if negate else ''
                    else:
                        # Non-constant axis - default to Blender Z (N64 Y rotation)
                        idx, negate = n64_utils.N64_AXIS_ROTATION_MAP['z']
                        subs['axis_index'] = str(idx)
                        subs['angle_sign'] = '-' if negate else ''
            else:
                subs[arg_name] = self.generate(arg)

            subs[f'arg{i}'] = subs.get(arg_name, self.generate(arg))

        return subs

    def _get_const_value(self, node: Dict) -> float:
        """Extract constant numeric value from AST node, or None if not constant."""
        if node is None:
            return None
        node_type = node.get('type')
        if node_type == 'int':
            return float(node.get('value', 0))
        elif node_type == 'float':
            return float(node.get('value', 0.0))
        elif node_type == 'unop' and node.get('op') == '-':
            inner = self._get_const_value(node.get('expr'))
            return -inner if inner is not None else None
        return None

    def _gen_new(self, node: Dict) -> str:
        type_name = node.get('typeName', '')
        args = node.get('args') or []

        if type_name == 'Vec4' and len(args) >= 3:
            x = self.generate(args[0])
            y = self.generate(args[1])
            z = self.generate(args[2])
            # Return a C99 compound literal for Vec4
            # This can be used in expressions but assignments are handled specially
            return f'(Vec3){{{x}, {y}, {z}}}'

        arg_strs = [self.generate(a) for a in args if a]
        return f'{type_name}({", ".join(arg_strs)})'


# =============================================================================
# Statement Generator
# =============================================================================

class StatementGenerator:
    """Generates C code from JSON statement nodes."""

    def __init__(self, ctx: GeneratorContext):
        self.ctx = ctx
        self.expr_gen = ExpressionGenerator(ctx)

    def generate(self, node: Dict) -> List[str]:
        """Generate C code lines for a statement node."""
        if node is None:
            return []

        node_type = node.get('type')

        if node_type == 'if':
            return self._gen_if(node)
        elif node_type == 'while':
            return self._gen_while(node)
        elif node_type == 'do_while':
            return self._gen_do_while(node)
        elif node_type == 'for':
            return self._gen_for(node)
        elif node_type == 'vars':
            return self._gen_vars(node)
        elif node_type == 'break':
            return [f'{self.ctx.indent_str()}break;']
        elif node_type == 'continue':
            return [f'{self.ctx.indent_str()}continue;']
        elif node_type == 'binop' and node.get('op') == '=':
            return self._gen_assignment(node)
        elif node_type == 'call':
            return self._gen_call_stmt(node)
        else:
            # Try as expression statement
            code = self.expr_gen.generate(node)
            if code and not code.startswith('/*'):
                return [f'{self.ctx.indent_str()}{code};']
            return []

    def _gen_if(self, node: Dict) -> List[str]:
        indent = self.ctx.indent_str()
        lines = []

        cond = self.expr_gen.generate(node.get('condition'))
        lines.append(f'{indent}if ({cond}) {{')

        self.ctx.indent += 1
        for stmt in (node.get('then') or []):
            lines.extend(self.generate(stmt))
        self.ctx.indent -= 1

        else_stmts = node.get('else_')
        if else_stmts:
            lines.append(f'{indent}}} else {{')
            self.ctx.indent += 1
            for stmt in else_stmts:
                lines.extend(self.generate(stmt))
            self.ctx.indent -= 1

        lines.append(f'{indent}}}')
        return lines

    def _gen_while(self, node: Dict) -> List[str]:
        """Generate C while loop."""
        indent = self.ctx.indent_str()
        lines = []

        cond = self.expr_gen.generate(node.get('condition'))
        lines.append(f'{indent}while ({cond}) {{')

        self.ctx.indent += 1
        for stmt in (node.get('body') or []):
            lines.extend(self.generate(stmt))
        self.ctx.indent -= 1

        lines.append(f'{indent}}}')
        return lines

    def _gen_do_while(self, node: Dict) -> List[str]:
        """Generate C do-while loop."""
        indent = self.ctx.indent_str()
        lines = []

        lines.append(f'{indent}do {{')

        self.ctx.indent += 1
        for stmt in (node.get('body') or []):
            lines.extend(self.generate(stmt))
        self.ctx.indent -= 1

        cond = self.expr_gen.generate(node.get('condition'))
        lines.append(f'{indent}}} while ({cond});')
        return lines

    def _gen_for(self, node: Dict) -> List[str]:
        """Generate C for loop from Haxe for-in loop."""
        indent = self.ctx.indent_str()
        lines = []

        iterator = node.get('iterator', {})
        iter_type = iterator.get('type', '')
        var_name = iterator.get('varName', 'i')

        if iter_type == 'range':
            # for (i in 0...n) -> for (int i = start; i < end; i++)
            start = self.expr_gen.generate(iterator.get('start'))
            end = self.expr_gen.generate(iterator.get('end'))
            lines.append(f'{indent}for (int {var_name} = {start}; {var_name} < {end}; {var_name}++) {{')
        else:
            # General iterator - not fully supported, emit warning
            log.warn(f'General iterators not fully supported, using placeholder')
            lines.append(f'{indent}/* TODO: iterator loop */ {{')

        self.ctx.indent += 1
        for stmt in (node.get('body') or []):
            lines.extend(self.generate(stmt))
        self.ctx.indent -= 1

        lines.append(f'{indent}}}')
        return lines

    def _gen_vars(self, node: Dict) -> List[str]:
        """Generate C local variable declarations from Haxe var statements."""
        indent = self.ctx.indent_str()
        lines = []

        vars_list = node.get('vars', [])

        # Debug: log vars being processed
        if not vars_list:
            log.warn(f'_gen_vars called but no vars list in node: {node}')

        for var_info in vars_list:
            var_name = var_info.get('name', '')
            var_expr = var_info.get('expr')

            if not var_name:
                log.warn(f'Variable declaration with empty name: {var_info}')
                continue

            # Track this as a local variable
            self.ctx.local_vars.add(var_name)

            if var_expr is not None:
                # Check if this is a Vec4 type assignment
                is_vec4 = self._is_vec4_expr(var_expr)

                if is_vec4:
                    # Track as Vec4 variable
                    self.ctx.vec4_vars.add(var_name)
                    vec_init = self._gen_vec4_var_init(var_name, var_expr, indent)
                    lines.extend(vec_init)
                else:
                    # Infer C type from the expression
                    c_type = self._infer_c_type(var_expr)
                    value = self.expr_gen.generate(var_expr)
                    lines.append(f'{indent}{c_type} {var_name} = {value};')
            else:
                # Uninitialized variable - default to float
                lines.append(f'{indent}float {var_name};')

        return lines

    def _is_vec4_expr(self, expr: Dict) -> bool:
        """Check if expression results in a Vec4 type."""
        if not expr:
            return False

        expr_type = expr.get('type')

        # new Vec4(...)
        if expr_type == 'new' and expr.get('typeName') == 'Vec4':
            return True

        # Field access to transform.scale, transform.loc, etc.
        if expr_type == 'field':
            field = expr.get('field', '')
            if field in ('scale', 'loc', 'location', 'dim'):
                return True
            # Check for nested field like object.transform.scale
            obj = expr.get('object')
            if obj and obj.get('type') == 'field':
                parent_field = obj.get('field', '')
                if parent_field == 'transform' and field in ('scale', 'loc', 'location', 'dim'):
                    return True

        return False

    def _gen_vec4_var_init(self, var_name: str, expr: Dict, indent: str) -> List[str]:
        """Generate initialization for a Vec4 local variable."""
        lines = []

        # Declare as a simple struct with x, y, z
        lines.append(f'{indent}struct {{ float x, y, z; }} {var_name};')

        expr_type = expr.get('type')

        # new Vec4(x, y, z)
        if expr_type == 'new' and expr.get('typeName') == 'Vec4':
            args = expr.get('args') or []
            if len(args) >= 3:
                x = self.expr_gen.generate(args[0])
                y = self.expr_gen.generate(args[1])
                z = self.expr_gen.generate(args[2])
                lines.append(f'{indent}{var_name}.x = {x};')
                lines.append(f'{indent}{var_name}.y = {y};')
                lines.append(f'{indent}{var_name}.z = {z};')

        # Field access like object.transform.scale
        elif expr_type == 'field':
            field = expr.get('field', '')
            obj = expr.get('object')

            # Determine source array
            if obj and obj.get('type') == 'field' and obj.get('field') == 'transform':
                self.ctx.needs_obj = True
                if field == 'scale':
                    lines.append(f'{indent}{var_name}.x = obj->transform.scale[0];')
                    lines.append(f'{indent}{var_name}.y = obj->transform.scale[1];')
                    lines.append(f'{indent}{var_name}.z = obj->transform.scale[2];')
                elif field in ('loc', 'location'):
                    lines.append(f'{indent}{var_name}.x = obj->transform.loc[0];')
                    lines.append(f'{indent}{var_name}.y = obj->transform.loc[1];')
                    lines.append(f'{indent}{var_name}.z = obj->transform.loc[2];')
                else:
                    # Generic field
                    src = self.expr_gen.generate(expr)
                    lines.append(f'{indent}{var_name}.x = {src}[0];')
                    lines.append(f'{indent}{var_name}.y = {src}[1];')
                    lines.append(f'{indent}{var_name}.z = {src}[2];')

        return lines

    def _infer_c_type(self, expr: Dict) -> str:
        """Infer C type from expression node."""
        if expr is None:
            return 'float'

        expr_type = expr.get('type')

        if expr_type == 'int':
            return 'int'
        elif expr_type == 'float':
            return 'float'
        elif expr_type == 'string':
            return 'const char*'
        elif expr_type == 'binop':
            # For binary operations, check operands
            left_type = self._infer_c_type(expr.get('left'))
            right_type = self._infer_c_type(expr.get('right'))
            # Float takes precedence
            if left_type == 'float' or right_type == 'float':
                return 'float'
            return 'int'
        elif expr_type == 'field':
            # Field access - check for known types
            field = expr.get('field', '')
            obj = expr.get('object', {})

            # Time.delta is float
            if obj.get('type') == 'ident' and obj.get('name') == 'Time' and field == 'delta':
                return 'float'

            # transform.x/y/z are float
            if field in ('x', 'y', 'z', 'w'):
                return 'float'

            # Default to float for unknown fields
            return 'float'
        elif expr_type == 'ident':
            # Check if it's a known member
            name = expr.get('name', '')
            if name in self.ctx.member_names:
                # Would need type info from member definitions
                return 'float'
            if name in self.ctx.local_vars:
                return 'float'  # Already declared, use same type
            return 'float'
        elif expr_type == 'unop':
            return self._infer_c_type(expr.get('expr'))
        else:
            return 'float'

    def _gen_assignment(self, node: Dict) -> List[str]:
        indent = self.ctx.indent_str()
        left = node.get('left')
        right = node.get('right')

        target = self.expr_gen.generate(left)

        # Skip no-op assignments
        if target.startswith('/*'):
            return []

        # Handle Vec4/Vec3 assignment to transform.scale, transform.loc, etc.
        # Check if target is obj->transform.scale or similar
        if self._is_transform_vec_property(left):
            return self._gen_transform_vec_assignment(indent, left, right)

        # Handle assignment of Vec4 variable to another Vec4 property
        if right and right.get('type') == 'new' and right.get('typeName') == 'Vec4':
            # new Vec4(x, y, z) assignment
            args = right.get('args') or []
            if len(args) >= 3:
                x = self.expr_gen.generate(args[0])
                y = self.expr_gen.generate(args[1])
                z = self.expr_gen.generate(args[2])
                # If assigning to a simple identifier (local var), create struct
                if left and left.get('type') == 'ident':
                    var_name = left.get('name', '')
                    return [
                        f'{indent}{var_name}.x = {x};',
                        f'{indent}{var_name}.y = {y};',
                        f'{indent}{var_name}.z = {z};',
                    ]

        # Handle assignment of Vec4 identifier to transform property
        if right and right.get('type') == 'ident' and self._is_transform_vec_property(left):
            return self._gen_transform_vec_assignment(indent, left, right)

        value = self.expr_gen.generate(right)

        # Skip no-op values
        if value.startswith('/*'):
            return []

        return [f'{indent}{target} = {value};']

    def _is_transform_vec_property(self, node: Dict) -> bool:
        """Check if node is a transform vector property like obj->transform.scale"""
        if not node or node.get('type') != 'field':
            return False
        field = node.get('field', '')
        if field not in ('scale', 'loc', 'location'):
            return False
        obj = node.get('object')
        if obj and obj.get('type') == 'field' and obj.get('field') == 'transform':
            return True
        return False

    def _gen_transform_vec_assignment(self, indent: str, left: Dict, right: Dict) -> List[str]:
        """Generate assignment to transform vector property (scale, loc)."""
        field = left.get('field', '')

        # Determine the C array name and if scale factor is needed
        # Scale factor converts Blender units (1.0 = normal) to N64 units (0.015 = normal)
        is_scale = field == 'scale'
        scale_factor = '0.015f' if is_scale else ''

        if is_scale:
            arr_name = 'obj->transform.scale'
        elif field in ('loc', 'location'):
            arr_name = 'obj->transform.loc'
        else:
            arr_name = f'obj->transform.{field}'

        self.ctx.needs_obj = True
        lines = []

        def format_component(expr: str) -> str:
            """Apply scale factor if this is a scale assignment."""
            if scale_factor:
                return f'({expr}) * {scale_factor}'
            return expr

        # Handle new Vec4(x, y, z)
        if right and right.get('type') == 'new' and right.get('typeName') == 'Vec4':
            args = right.get('args') or []
            if len(args) >= 3:
                x = self.expr_gen.generate(args[0])
                y = self.expr_gen.generate(args[1])
                z = self.expr_gen.generate(args[2])
                lines.append(f'{indent}{arr_name}[0] = {format_component(x)};')
                lines.append(f'{indent}{arr_name}[1] = {format_component(y)};')
                lines.append(f'{indent}{arr_name}[2] = {format_component(z)};')
                # Note: dirty flag should be set by buildMatrix() call
                return lines

        # Handle identifier (local Vec4 variable or member)
        if right and right.get('type') == 'ident':
            var_name = right.get('name', '')
            # Check if it's a member variable
            if var_name in self.ctx.member_names:
                self.ctx.needs_data = True
                lines.append(f'{indent}{arr_name}[0] = {format_component(f"tdata->{var_name}.x")};')
                lines.append(f'{indent}{arr_name}[1] = {format_component(f"tdata->{var_name}.y")};')
                lines.append(f'{indent}{arr_name}[2] = {format_component(f"tdata->{var_name}.z")};')
            else:
                # Local variable
                lines.append(f'{indent}{arr_name}[0] = {format_component(f"{var_name}.x")};')
                lines.append(f'{indent}{arr_name}[1] = {format_component(f"{var_name}.y")};')
                lines.append(f'{indent}{arr_name}[2] = {format_component(f"{var_name}.z")};')
            # Note: dirty flag should be set by buildMatrix() call
            return lines

        # Handle field access (e.g., someObject.scale)
        if right and right.get('type') == 'field':
            src = self.expr_gen.generate(right)
            lines.append(f'{indent}{arr_name}[0] = {format_component(f"{src}.x")};')
            lines.append(f'{indent}{arr_name}[1] = {format_component(f"{src}.y")};')
            lines.append(f'{indent}{arr_name}[2] = {format_component(f"{src}.z")};')
            # Note: dirty flag should be set by buildMatrix() call
            return lines

        # Fallback - shouldn't normally reach here
        value = self.expr_gen.generate(right)
        return [f'{indent}/* TODO: vec assignment */ {arr_name} = {value};']

    def _gen_call_stmt(self, node: Dict) -> List[str]:
        indent = self.ctx.indent_str()
        code = self.expr_gen.generate(node)
        if code.startswith('/*'):
            return []
        return [f'{indent}{code};']


# =============================================================================
# Trait Code Generator
# =============================================================================

class TraitCodeGenerator:
    """Generates N64 C code for a single trait from JSON data."""

    def __init__(self, name: str, trait_data: Dict, scene_map: Dict[str, str] = None):
        self.name = name
        self.data = trait_data
        self.scene_map = scene_map or {}
        self.func_name = safesrc(name).lower()
        self.members = {m.get('name'): m for m in trait_data.get('members', [])}
        self.member_names = set(self.members.keys())

    def generate_data_struct(self) -> str:
        """Generate the trait data struct definition."""
        fields = []

        # Check if we need scene field
        if self._needs_scene_field():
            fields.append('    SceneId target_scene;')

        # Add member fields (macro provides ctype directly)
        for member_info in self.data.get('members', []):
            name = member_info.get('name', '')
            c_type = member_info.get('ctype', 'int32_t')
            fields.append(f'    {c_type} {name};')

        if not fields:
            return ''

        return f'typedef struct {{\n' + '\n'.join(fields) + f'\n}} {self.name}Data;\n'

    def _needs_scene_field(self) -> bool:
        """Check if trait needs a scene target field."""
        func_data = self.data.get('functions', {})
        for lifecycle in ['init', 'update', 'remove']:
            stmts = func_data.get(lifecycle, [])
            if stmts and self._stmts_use_scene_var(stmts):
                return True
        return False

    def _stmts_use_scene_var(self, stmts: List[Dict]) -> bool:
        """Check if statements use Scene.setActive with a variable (not a string literal)."""
        if not stmts:
            return False
        for stmt in stmts:
            if not stmt:
                continue
            if stmt.get('type') == 'call':
                path = stmt.get('path', '')
                if 'Scene' in path and 'setActive' in path:
                    args = stmt.get('args', [])
                    if args:
                        arg = args[0]
                        # If arg is a variable (ident), we need a scene field to store it
                        if arg and arg.get('type') == 'ident':
                            return True
            elif stmt.get('type') == 'if':
                then_stmts = stmt.get('then') or []
                else_stmts = stmt.get('else_') or []
                if self._stmts_use_scene_var(then_stmts):
                    return True
                if self._stmts_use_scene_var(else_stmts):
                    return True
        return False

    def generate_declarations(self) -> List[str]:
        """Generate function declarations."""
        return [
            f'void {self.func_name}_on_ready(void *entity, void *data);',
            f'void {self.func_name}_on_update(void *entity, float dt, void *data);',
            f'void {self.func_name}_on_remove(void *entity, void *data);',
        ]

    def generate_implementation(self) -> str:
        """Generate the trait implementation using the template."""
        template = load_template('trait_impl.c.j2')
        if not template:
            # Fallback if template not found
            return self._generate_implementation_fallback()

        func_data = self.data.get('functions', {})

        on_ready_code = self._gen_lifecycle_body(func_data.get('init'), has_dt=False)
        on_update_code = self._gen_lifecycle_body(func_data.get('update'), has_dt=True)
        on_remove_code = self._gen_lifecycle_body(func_data.get('remove'), has_dt=False)

        return apply_template(
            template,
            trait_class=self.name,
            func_name=self.func_name,
            on_ready_code=on_ready_code,
            on_update_code=on_update_code,
            on_remove_code=on_remove_code,
        )

    def _gen_lifecycle_body(self, stmts: List[Dict], has_dt: bool) -> str:
        """Generate the body code for a lifecycle function."""
        ctx = GeneratorContext(
            trait_name=self.name,
            func_name=self.func_name,
            member_names=self.member_names,
            indent=1
        )

        # Generate statements
        body_lines = []
        if stmts:
            stmt_gen = StatementGenerator(ctx)
            for stmt in stmts:
                body_lines.extend(stmt_gen.generate(stmt))

        # Build declarations needed
        decl_lines = []
        if ctx.needs_obj:
            decl_lines.append('    ArmObject *obj = (ArmObject *)entity;')
        if ctx.needs_data:
            decl_lines.append(f'    {self.name}Data *tdata = ({self.name}Data *)data;')

        # Combine declarations and body
        all_lines = decl_lines
        if body_lines:
            if decl_lines:
                all_lines.append('')
            all_lines.extend(body_lines)

        return '\n'.join(all_lines)

    def _generate_implementation_fallback(self) -> str:
        """Fallback implementation generation if template not found."""
        func_data = self.data.get('functions', {})
        lines = [f'// Trait: {self.name}']

        for lifecycle, has_dt in [('on_ready', False), ('on_update', True), ('on_remove', False)]:
            func_key = {'on_ready': 'init', 'on_update': 'update', 'on_remove': 'remove'}[lifecycle]

            if has_dt:
                sig = f'void {self.func_name}_{lifecycle}(void *entity, float dt, void *data)'
            else:
                sig = f'void {self.func_name}_{lifecycle}(void *entity, void *data)'

            lines.append(f'{sig} {{')
            lines.append('    (void)entity;')
            if has_dt:
                lines.append('    (void)dt;')
            lines.append('    (void)data;')

            body = self._gen_lifecycle_body(func_data.get(func_key), has_dt)
            if body.strip():
                lines.append(body)

            lines.append('}')
            lines.append('')

        return '\n'.join(lines)


# =============================================================================
# Main Generator
# =============================================================================

class TraitsGenerator:
    """Main generator that produces traits.h and traits.c files."""

    def __init__(self, traits_data: Dict[str, Dict], scene_map: Dict[str, str] = None):
        self.traits_data = traits_data
        self.scene_map = scene_map or {}
        self.trait_generators = {}

        for name, data in traits_data.items():
            self.trait_generators[name] = TraitCodeGenerator(name, data, scene_map)

    def generate_header(self, data_instances: List[Tuple[str, str, str]] = None) -> str:
        """Generate traits.h content using the template."""
        template = load_template('traits.h.j2')
        if not template:
            return self._generate_header_fallback(data_instances)

        # Collect all data structs
        structs = []
        for name in sorted(self.trait_generators.keys()):
            gen = self.trait_generators[name]
            struct = gen.generate_data_struct()
            if struct:
                structs.append(struct)

        # Collect all declarations
        declarations = []
        for name in sorted(self.trait_generators.keys()):
            gen = self.trait_generators[name]
            declarations.extend(gen.generate_declarations())

        # Collect extern declarations for data instances
        externs = []
        if data_instances:
            for var_name, type_name, _ in data_instances:
                externs.append(f'extern {type_name} {var_name};')

        return apply_template(
            template,
            trait_data_structs='\n'.join(structs),
            trait_data_externs='\n'.join(externs),
            trait_declarations='\n'.join(declarations),
        )

    def generate_source(self, data_instances: List[Tuple[str, str, str]] = None) -> str:
        """Generate traits.c content using the template."""
        template = load_template('traits.c.j2')
        if not template:
            return self._generate_source_fallback(data_instances)

        # Collect data definitions
        definitions = []
        if data_instances:
            for var_name, type_name, init_str in data_instances:
                if init_str:
                    # Escape braces for apply_template: {{ becomes { after processing
                    escaped_init = init_str.replace('{', '{{').replace('}', '}}')
                    # Generate mutable instance only (reset happens inline in scene_init)
                    definitions.append(f'{type_name} {var_name} = {{{{{escaped_init}}}}};')
                else:
                    definitions.append(f'{type_name} {var_name} = {{{{0}}}};')

        # Collect all implementations
        implementations = []
        for name in sorted(self.trait_generators.keys()):
            gen = self.trait_generators[name]
            implementations.append(gen.generate_implementation())

        return apply_template(
            template,
            trait_data_definitions='\n'.join(definitions),
            trait_implementations='\n'.join(implementations),
        )

    def _generate_header_fallback(self, data_instances) -> str:
        """Fallback header generation."""
        lines = ['#pragma once', '', '#include "scenes.h"', '#include "../types.h"', '']

        # Data structs
        for name in sorted(self.trait_generators.keys()):
            struct = self.trait_generators[name].generate_data_struct()
            if struct:
                lines.append(struct)

        # Extern declarations
        if data_instances:
            for var_name, type_name, _ in data_instances:
                lines.append(f'extern {type_name} {var_name};')
            lines.append('')

        # Function declarations
        for name in sorted(self.trait_generators.keys()):
            for decl in self.trait_generators[name].generate_declarations():
                lines.append(decl)

        return '\n'.join(lines)

    def _generate_source_fallback(self, data_instances) -> str:
        """Fallback source generation."""
        lines = ['#include "traits.h"', '#include "scenes.h"', '#include "../types.h"',
                 '#include "../iron/object/transform.h"', '#include "../iron/system/input.h"', '']

        # Data definitions
        if data_instances:
            for var_name, type_name, init_str in data_instances:
                if init_str:
                    # Generate mutable instance only (reset happens inline in scene_init)
                    lines.append(f'{type_name} {var_name} = {{{init_str}}};')
                else:
                    lines.append(f'{type_name} {var_name} = {{0}};')
            lines.append('')

        # Implementations
        for name in sorted(self.trait_generators.keys()):
            lines.append(self.trait_generators[name].generate_implementation())

        return '\n'.join(lines)


# =============================================================================
# Macro JSON Loading
# =============================================================================

def get_macro_json_path() -> str:
    """Get the path to n64_traits.json."""
    if HAS_ARM:
        build_dir = arm.utils.build_dir()
    else:
        build_dir = '.'
    return os.path.join(build_dir, 'n64_traits.json')


def load_macro_json() -> Optional[Dict]:
    """Load trait metadata JSON from macro."""
    json_path = get_macro_json_path()
    if not os.path.exists(json_path):
        log.warn(f'Macro JSON not found at {json_path}')
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log.warn(f'Failed to load macro JSON: {e}')
        return None


def json_to_summary(macro_data: Dict) -> Dict:
    """Convert macro JSON to summary format for exporter."""
    summary = {
        'traits': {},
        'input_buttons': set(),
        'has_transform': False,
        'has_scene': False,
        'has_time': False,
        'scene_names': set(),
    }

    traits_data = macro_data.get('traits', {})

    for name, trait_data in traits_data.items():
        api_calls = trait_data.get('apiCalls', {})

        # Extract members (macro provides ctype directly)
        members = {}
        member_values = {}
        for member_info in trait_data.get('members', []):
            member_name = member_info.get('name', '')
            c_type = member_info.get('ctype', 'int32_t')
            default_val = member_info.get('defaultValue')

            members[member_name] = c_type
            if default_val is not None:
                member_values[member_name] = default_val

        trait_summary = {
            'members': members,
            'member_values': member_values,
            'functions': {},
            'input_calls': [],
            'transform_calls': [],
            'scene_calls': [],
        }

        # Process functions - use class name from trait data
        class_name = trait_data.get('name', name)
        func_data = trait_data.get('functions', {})
        for lifecycle in ['init', 'update', 'remove']:
            if func_data.get(lifecycle):
                trait_summary['functions'][lifecycle] = {'name': f'{safesrc(class_name).lower()}_on_{lifecycle}'}

        # Process input calls
        for input_call in (api_calls.get('input') or []):
            method = input_call.get('type', 'down')
            button = 'a'
            args = input_call.get('args') or []
            if args and args[0] and isinstance(args[0], dict):
                first_arg = args[0]
                if first_arg.get('type') == 'ident':
                    button = first_arg.get('name', 'a')
                elif first_arg.get('type') == 'field':
                    button = first_arg.get('field', 'a')

            trait_summary['input_calls'].append({
                'method': method.lower(),
                'button': button.lower(),
                'lifecycle': 'update',
            })
            summary['input_buttons'].add(button.lower())

        # Process transform calls
        for transform_call in (api_calls.get('transform') or []):
            method = transform_call.get('method', 'rotate')
            trait_summary['transform_calls'].append({
                'method': method.lower(),
                'lifecycle': 'update',
            })
            summary['has_transform'] = True

        # Process scene calls
        for scene_call in (api_calls.get('scene') or []):
            method = scene_call.get('method', 'setActive')
            scene_name = 'unknown'
            args = scene_call.get('args') or []
            if args and args[0] and isinstance(args[0], dict):
                first_arg = args[0]
                if first_arg.get('type') == 'string':
                    scene_name = first_arg.get('value', 'unknown')

            trait_summary['scene_calls'].append({
                'method': method.lower(),
                'scene_name': scene_name,
                'lifecycle': 'update',
            })
            summary['has_scene'] = True
            summary['scene_names'].add(scene_name)

        if api_calls.get('time'):
            summary['has_time'] = True

        summary['traits'][name] = trait_summary

    summary['input_buttons'] = list(summary['input_buttons'])
    summary['scene_names'] = list(summary['scene_names'])

    return summary


def scan_and_summarize() -> Dict:
    """Load and process trait metadata from macro JSON.

    Returns summary dict with:
        - traits: Per-trait info (members, functions, calls)
        - input_buttons: List of used buttons
        - has_transform: Whether transform ops are used
        - has_scene: Whether scene switching is used
        - has_time: Whether Time API is used
        - scene_names: List of referenced scene names
    """
    macro_data = load_macro_json()

    if not macro_data:
        log.warn('No macro JSON found')
        return {'traits': {}, 'input_buttons': [], 'has_transform': False,
                'has_scene': False, 'has_time': False, 'scene_names': []}

    # Log traits found
    for name, trait_data in macro_data.get('traits', {}).items():
        func_data = trait_data.get('functions', {})
        has_funcs = any(func_data.get(lc) for lc in ['init', 'update', 'remove'])
        if has_funcs:
            log.info(f'Loaded trait {name}')
        else:
            log.warn(f'Trait {name} has no functions, will use scaffold')

    return json_to_summary(macro_data)


# =============================================================================
# Public API
# =============================================================================

def write_traits_files(
    trait_classes: Set[str],
    trait_data_instances: List[Tuple[str, str, str]],
    scene_map: Dict[str, str] = None
) -> bool:
    """Generate and write trait C files."""
    if HAS_ARM:
        output_dir = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data')
    else:
        output_dir = './src/data'

    os.makedirs(output_dir, exist_ok=True)

    # Load trait data from macro JSON
    macro_data = load_macro_json()
    if not macro_data:
        log.warn('No macro JSON found for trait generation')
        macro_data = {'traits': {}}

    traits = macro_data.get('traits', {})

    # Filter to requested traits
    traits_to_generate = {k: v for k, v in traits.items() if k in trait_classes}

    # Create generator
    generator = TraitsGenerator(traits_to_generate, scene_map)

    # Add scaffolds for traits without macro data
    scaffold_traits = trait_classes - set(traits.keys())
    scaffold_decls = []
    scaffold_impls = []

    for trait_class in sorted(scaffold_traits):
        func_name = safesrc(trait_class).lower()
        scaffold_decls.extend([
            f'void {func_name}_on_ready(void *entity, void *data);',
            f'void {func_name}_on_update(void *entity, float dt, void *data);',
            f'void {func_name}_on_remove(void *entity, void *data);',
        ])

        scaffold_impls.append(f'''// Trait: {trait_class} (scaffold)
void {func_name}_on_ready(void *entity, void *data) {{
    (void)entity;
    (void)data;
}}

void {func_name}_on_update(void *entity, float dt, void *data) {{
    (void)entity;
    (void)dt;
    (void)data;
}}

void {func_name}_on_remove(void *entity, void *data) {{
    (void)entity;
    (void)data;
}}
''')

    # Generate header
    header_content = generator.generate_header(trait_data_instances)
    if scaffold_decls:
        header_content += '\n' + '\n'.join(scaffold_decls) + '\n'

    # Generate source
    source_content = generator.generate_source(trait_data_instances)
    if scaffold_impls:
        source_content += '\n' + '\n'.join(scaffold_impls)

    # Write files
    header_path = os.path.join(output_dir, 'traits.h')
    with open(header_path, 'w', encoding='utf-8') as f:
        f.write(header_content)

    source_path = os.path.join(output_dir, 'traits.c')
    with open(source_path, 'w', encoding='utf-8') as f:
        f.write(source_content)

    log.info(f'Generated traits: {", ".join(sorted(traits_to_generate.keys()))}')
    return True
