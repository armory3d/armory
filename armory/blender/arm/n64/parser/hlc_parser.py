"""
HLC Parser - AST-based HashLink C Parser

Parses HashLink C output into AST nodes for accurate translation to N64 C code.
This replaces the pattern-based approach with proper parsing.
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# Handle both standalone and Blender module imports
try:
    from .ast import (
        Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast,
        ExprStmt, Assignment, IfStmt, ReturnStmt,
        TraitMember, TraitFunction, TraitAST,
        Expr, Stmt, literal_from_value
    )
    from ..config import get_config, get_skip_member_names, get_skip_type_prefixes
except ImportError:
    from ast import (
        Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast,
        ExprStmt, Assignment, IfStmt, ReturnStmt,
        TraitMember, TraitFunction, TraitAST,
        Expr, Stmt, literal_from_value
    )
    from config import get_config, get_skip_member_names, get_skip_type_prefixes

# Try to import arm modules (only available in Blender context)
try:
    import arm
    import arm.utils
    import arm.log as log
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False
    class MockLog:
        @staticmethod
        def info(msg): print(f"[INFO] {msg}")
        @staticmethod
        def warn(msg): print(f"[WARN] {msg}")
        @staticmethod
        def error(msg): print(f"[ERROR] {msg}")
    log = MockLog()


# =============================================================================
# Register Tracking
# =============================================================================

@dataclass
class RegisterState:
    """
    Tracks what value each HLC register (r0, r1, etc.) holds.

    HLC uses registers like:
        r1 = r0->speed;      // r1 now holds MemberAccess('self', 'speed')
        r2 = 5.;             // r2 now holds Literal(5.0)
        r3 = r1 * r2;        // r3 now holds BinaryOp('*', ...)
    """
    values: Dict[str, Expr] = field(default_factory=dict)

    def set(self, reg: str, value: Expr):
        """Set register value."""
        self.values[reg] = value

    def get(self, reg: str) -> Optional[Expr]:
        """Get register value, returns Variable if unknown."""
        return self.values.get(reg, Variable(reg))

    def clear(self):
        """Clear all register values."""
        self.values.clear()


# =============================================================================
# Parsing Patterns
# =============================================================================

# Variable declarations at function start
VAR_DECL_PATTERN = re.compile(
    r'^\s*(\w[\w\s\*]+?)\s+(\w+(?:\s*,\s*\w+)*)\s*;',
    re.MULTILINE
)

# Local variable assignment: r1 = value;
LOCAL_ASSIGN_PATTERN = re.compile(
    r'(\w+)\s*=\s*([^;]+);'
)

# Member access: r0->member
MEMBER_ACCESS_PATTERN = re.compile(
    r'(\w+)->(\w+)'
)

# String constant: (String)s$name
STRING_CONST_PATTERN = re.compile(
    r'\(String\)s\$(\w+)'
)

# Numeric literal (int or float)
NUMERIC_PATTERN = re.compile(
    r'^-?[\d.]+(?:e[+-]?\d+)?$',
    re.IGNORECASE
)

# Cast: (type)expr
CAST_PATTERN = re.compile(
    r'\((\w+)\)(\w+)'
)

# Goto label: goto label$xxx;
GOTO_PATTERN = re.compile(
    r'goto\s+(label\$[\w]+)\s*;'
)

# Label definition: label$xxx:
LABEL_DEF_PATTERN = re.compile(
    r'^(label\$[\w]+):',
    re.MULTILINE
)

# If statement: if( cond ) goto label;
IF_GOTO_PATTERN = re.compile(
    r'if\s*\(\s*([^)]+)\s*\)\s*goto\s+(label\$[\w]+)\s*;'
)

# If statement (negated): if( !cond ) goto label;
IF_NOT_GOTO_PATTERN = re.compile(
    r'if\s*\(\s*!\s*(\w+)\s*\)\s*goto\s+(label\$[\w]+)\s*;'
)

# NOTE: IRON_PATTERNS moved to api_mappings.json - loaded via config.loader

# Binary operators
BINARY_OP_PATTERN = re.compile(
    r'(\w+)\s*([\+\-\*\/\%]|==|!=|<=|>=|<|>|&&|\|\|)\s*(\w+)'
)


# =============================================================================
# Expression Parser
# =============================================================================

class ExpressionParser:
    """Parses HLC expressions into AST nodes."""

    def __init__(self, registers: RegisterState, string_consts: Dict[str, str]):
        self.registers = registers
        self.string_consts = string_consts  # Maps var -> string value

    def parse(self, expr_str: str) -> Expr:
        """Parse an expression string into an AST node."""
        expr_str = expr_str.strip()

        # String constant: (String)s$name
        match = STRING_CONST_PATTERN.match(expr_str)
        if match:
            return Literal(match.group(1), 'string')

        # Numeric literal
        if NUMERIC_PATTERN.match(expr_str):
            val = float(expr_str) if '.' in expr_str or 'e' in expr_str.lower() else int(expr_str)
            return Literal(val, 'double' if isinstance(val, float) else 'int')

        # NULL
        if expr_str == 'NULL':
            return Literal(None, 'null')

        # Member access: r0->member
        match = MEMBER_ACCESS_PATTERN.match(expr_str)
        if match:
            obj_reg = match.group(1)
            member = match.group(2)
            # r0 is always 'self' (the trait instance)
            if obj_reg == 'r0':
                return MemberAccess('self', member)
            else:
                # Resolve what object the register holds
                obj_expr = self.registers.get(obj_reg)
                if isinstance(obj_expr, MemberAccess):
                    # e.g., r7 = r0->object, then r7->transform
                    return MemberAccess(f'{obj_expr.object}.{obj_expr.member}', member)
                return MemberAccess(obj_reg, member)

        # Cast: (type)var
        match = CAST_PATTERN.match(expr_str)
        if match:
            cast_type = match.group(1)
            inner = match.group(2)
            inner_expr = self.parse(inner)
            # For simple float casts, just return the inner expression with type info
            if cast_type == 'float':
                if isinstance(inner_expr, Literal):
                    return Literal(float(inner_expr.value) if inner_expr.value else 0.0, 'float')
            return Cast(cast_type, inner_expr)

        # Binary operation: a op b
        match = BINARY_OP_PATTERN.match(expr_str)
        if match:
            left_str = match.group(1)
            op = match.group(2)
            right_str = match.group(3)
            left = self.resolve_value(left_str)
            right = self.resolve_value(right_str)
            return BinaryOp(op, left, right)

        # Simple variable reference
        if expr_str.isidentifier():
            return self.resolve_value(expr_str)

        # Unknown - return as variable
        return Variable(expr_str)

    def resolve_value(self, var_name: str) -> Expr:
        """Resolve a variable name to its value or AST node."""
        # Check string constants first
        if var_name in self.string_consts:
            return Literal(self.string_consts[var_name], 'string')

        # Check registers
        reg_value = self.registers.get(var_name)
        if reg_value and not isinstance(reg_value, Variable):
            return reg_value

        # Check if it's a numeric literal
        if NUMERIC_PATTERN.match(var_name):
            val = float(var_name) if '.' in var_name else int(var_name)
            return Literal(val, 'double' if isinstance(val, float) else 'int')

        return Variable(var_name)


# =============================================================================
# Function Body Parser
# =============================================================================

class FunctionParser:
    """Parses HLC function bodies into AST statements."""

    def __init__(self):
        self.registers = RegisterState()
        self.string_consts: Dict[str, str] = {}
        self.vec4_values: Dict[str, Vec3] = {}  # Maps Vec4 var to its x,y,z values
        self.expr_parser: ExpressionParser = None

    def parse_function(self, body: str, lifecycle: str, func_name: str) -> TraitFunction:
        """Parse a function body into a TraitFunction AST node."""
        self.registers.clear()
        self.string_consts.clear()
        self.vec4_values.clear()
        self.expr_parser = ExpressionParser(self.registers, self.string_consts)

        func = TraitFunction(func_name, lifecycle)

        # First pass: collect string constants and Vec4 constructions
        self._collect_constants(body)

        # Second pass: parse statements
        statements = self._parse_statements(body)
        func.statements = statements

        # Set metadata flags
        func.uses_delta = 'iron_system_Time_get_delta' in body
        func.uses_transform = 'iron_object_Transform_' in body
        func.uses_input = 'iron_system_Gamepad_' in body
        func.uses_scene = 'iron_Scene_setActive' in body

        return func

    def _collect_constants(self, body: str):
        """Collect Vec4 values from the function body.

        Note: String constants are collected inline during _parse_statements
        to handle register reuse correctly (when the same register is assigned
        different string values at different points).
        """
        # Find Vec4 constructions and their component values
        # Pattern: Vec4_new(r8, &r10, &r12, &r14, r16)
        # Preceded by: r10 = (float)r9; where r9 = 0 or 1

        # Track float pointer variables
        float_vals: Dict[str, float] = {}

        # Find: r9 = 0; or r9 = 1;
        for match in re.finditer(r'(\w+)\s*=\s*(\d+)\s*;', body):
            var = match.group(1)
            val = int(match.group(2))
            float_vals[var] = float(val)

        # Find: r10 = (float)r9;
        for match in re.finditer(r'(\w+)\s*=\s*\(float\)(\w+)\s*;', body):
            dest = match.group(1)
            src = match.group(2)
            if src in float_vals:
                float_vals[dest] = float_vals[src]

        # Find: r11 = &r10;
        ptr_to_val: Dict[str, str] = {}
        for match in re.finditer(r'(\w+)\s*=\s*&(\w+)\s*;', body):
            ptr_var = match.group(1)
            val_var = match.group(2)
            ptr_to_val[ptr_var] = val_var

        # Find Vec4_new calls: iron_math_Vec4_new(r8, r11, r13, r15, r16);
        for match in re.finditer(r'iron_math_Vec4_new\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\)', body):
            vec_var = match.group(1)
            x_ptr, y_ptr, z_ptr = match.group(2), match.group(3), match.group(4)

            # Resolve pointer -> value -> float
            x_val = float_vals.get(ptr_to_val.get(x_ptr, ''), 0.0)
            y_val = float_vals.get(ptr_to_val.get(y_ptr, ''), 0.0)
            z_val = float_vals.get(ptr_to_val.get(z_ptr, ''), 0.0)

            self.vec4_values[vec_var] = Vec3(
                Literal(x_val, 'float'),
                Literal(y_val, 'float'),
                Literal(z_val, 'float')
            )

    def _parse_statements(self, body: str) -> List[Stmt]:
        """Parse the function body into a list of statements."""
        statements: List[Stmt] = []
        lines = body.split('\n')

        # Pattern to detect string constant assignments: r4 = (String)s$a;
        string_const_pattern = re.compile(r'(\w+)\s*=\s*\(String\)s\$(\w+)\s*;')

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1

            if not line or line.startswith('//'):
                continue

            # Update string constants inline BEFORE parsing statements
            # This ensures each API call sees the correct value that was assigned before it
            str_match = string_const_pattern.match(line)
            if str_match:
                var = str_match.group(1)
                value = str_match.group(2)
                self.string_consts[var] = value
                continue  # This line is just a constant assignment, skip it

            # Skip variable declarations
            if self._is_var_declaration(line):
                continue

            # Skip null checks
            if 'hl_null_access()' in line:
                continue

            # Skip return
            if line == 'return;':
                continue

            # Skip label definitions
            if LABEL_DEF_PATTERN.match(line):
                continue

            # Parse if-goto (conditional)
            match = IF_GOTO_PATTERN.search(line)
            if match:
                condition_str = match.group(1)
                label = match.group(2)

                # Parse the condition
                condition = self._parse_condition(condition_str)

                # Collect statements until the label
                then_body = []
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith(label + ':'):
                        i += 1
                        break
                    if next_line and not next_line.startswith('//'):
                        stmt = self._parse_single_statement(next_line)
                        if stmt:
                            then_body.append(stmt)
                    i += 1

                # HLC uses inverted logic: if (cond == 0) goto skip; means if (cond) { body }
                # We need to negate the condition
                if then_body:
                    negated = self._negate_condition(condition)
                    statements.append(IfStmt(negated, then_body))
                continue

            # Parse if-not-goto
            match = IF_NOT_GOTO_PATTERN.search(line)
            if match:
                var = match.group(1)
                label = match.group(2)

                condition = self.expr_parser.resolve_value(var)

                # Collect statements until the label
                then_body = []
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith(label + ':'):
                        i += 1
                        break
                    if next_line and not next_line.startswith('//'):
                        stmt = self._parse_single_statement(next_line)
                        if stmt:
                            then_body.append(stmt)
                    i += 1

                # if (!var) goto label; means if (var) { body }
                if then_body:
                    statements.append(IfStmt(condition, then_body))
                continue

            # Parse regular statement
            stmt = self._parse_single_statement(line)
            if stmt:
                statements.append(stmt)

        return statements

    def _is_var_declaration(self, line: str) -> bool:
        """Check if a line is a variable declaration."""
        # Variable declarations have type followed by variable names
        decl_types = ['int', 'float', 'double', 'bool', 'String', 'vclosure',
                      'iron__', 'arm__', 'hl_', 'vdynamic', 'varray']
        for t in decl_types:
            if line.strip().startswith(t):
                return True
        # Also check for pointer declarations
        if '*' in line and '=' not in line and line.endswith(';'):
            return True
        return False

    def _parse_condition(self, cond_str: str) -> Expr:
        """Parse a condition expression."""
        cond_str = cond_str.strip()

        # r2 == r5 (comparison)
        match = re.match(r'(\w+)\s*(==|!=|<|>|<=|>=)\s*(\w+)', cond_str)
        if match:
            left = self.expr_parser.resolve_value(match.group(1))
            op = match.group(2)
            right = self.expr_parser.resolve_value(match.group(3))
            return BinaryOp(op, left, right)

        # !var (negation)
        match = re.match(r'!\s*(\w+)', cond_str)
        if match:
            inner = self.expr_parser.resolve_value(match.group(1))
            return UnaryOp('!', inner)

        # Single variable (truthy check)
        return self.expr_parser.resolve_value(cond_str)

    def _negate_condition(self, condition: Expr) -> Expr:
        """Negate a condition (for inverted HLC if-goto patterns)."""
        if isinstance(condition, BinaryOp):
            # r2 == r5 becomes r2 != r5, but we actually want the original condition
            # because HLC does: if (result == 0) goto skip; which means if (result != 0) { body }
            negate_map = {'==': '!=', '!=': '==', '<': '>=', '>': '<=', '<=': '>', '>=': '<'}
            if condition.op in negate_map:
                return BinaryOp(negate_map[condition.op], condition.left, condition.right)

        if isinstance(condition, UnaryOp) and condition.op == '!':
            return condition.operand

        return UnaryOp('!', condition)

    def _parse_single_statement(self, line: str) -> Optional[Stmt]:
        """Parse a single statement line."""
        line = line.strip()
        if not line or line.startswith('//'):
            return None

        # Skip labels and gotos
        if line.startswith('label$') or line.startswith('goto '):
            return None

        # Skip null checks and HL runtime calls
        if 'hl_null_access' in line or 'hl_alloc' in line:
            return None

        # Assignment: var = expr;
        match = re.match(r'(\w+(?:->\w+)?)\s*=\s*(.+);$', line)
        if match:
            target_str = match.group(1)
            value_str = match.group(2)

            # Parse target
            if '->' in target_str:
                parts = target_str.split('->')
                target = MemberAccess('self' if parts[0] == 'r0' else parts[0], parts[1])
            else:
                target = Variable(target_str)

            # Parse value - check for Iron API calls first
            value = self._parse_value_or_call(value_str)

            # Track register values
            if isinstance(target, Variable):
                self.registers.set(target.name, value)

            # Only emit assignment if it's to a member (not a temp register)
            if isinstance(target, MemberAccess):
                # Skip system members that shouldn't be in user code
                if target.member in get_skip_member_names():
                    return None
                # Skip if value is an unresolved HLC register (r0, r1, etc.)
                if isinstance(value, Variable) and re.match(r'^r\d+$', value.name):
                    return None
                return Assignment(target, value)

            return None

        # Standalone function call: func(args);
        call = self._try_parse_call(line.rstrip(';'))
        if call:
            return ExprStmt(call)

        return None

    def _parse_value_or_call(self, value_str: str) -> Expr:
        """Parse a value that might be a function call."""
        value_str = value_str.strip()

        # Check for Iron API calls
        call = self._try_parse_call(value_str)
        if call:
            return call

        # Check for binary operation
        match = re.match(r'(\w+)\s*([\+\-\*\/])\s*(\w+)$', value_str)
        if match:
            left = self.expr_parser.resolve_value(match.group(1))
            op = match.group(2)
            right = self.expr_parser.resolve_value(match.group(3))
            return BinaryOp(op, left, right)

        # Regular expression
        return self.expr_parser.parse(value_str)

    def _try_parse_call(self, expr_str: str) -> Optional[Call]:
        """Try to parse an expression as an Iron API call using config-driven patterns."""
        config = get_config()

        # Try to match against all configured API patterns
        result = config.find_matching_api(expr_str)
        if not result:
            return None

        api, match = result
        groups = match.groupdict()

        # Handle custom handlers (complex logic that can't be templated)
        if api.handler == 'custom':
            return self._handle_custom_api(api, groups)

        # Handle template-based APIs (simple pattern → output mapping)
        return self._handle_template_api(api, groups, config)

    def _handle_template_api(self, api, groups: dict, config) -> Optional[Call]:
        """Handle APIs that use simple template substitution."""
        target = api.target
        method = api.method

        # Build arguments based on API arg specs
        args = []
        for arg_spec in api.args:
            arg_name = arg_spec.get('name')
            arg_type = arg_spec.get('type')

            # Get raw value from regex group
            raw_value = groups.get(arg_name, '')

            # Resolve string constants
            if raw_value in self.string_consts:
                raw_value = self.string_consts[raw_value]

            # Apply value mapping if specified
            if arg_type and arg_type.endswith('_map'):
                mapped_value = config.map_value(arg_type, raw_value.lower(), raw_value)
                args.append(Literal(mapped_value, 'string'))
            else:
                args.append(Literal(raw_value, 'string'))

        return Call(target, method, args)

    def _handle_custom_api(self, api, groups: dict) -> Optional[Call]:
        """Handle APIs that need custom logic."""

        # Time.delta
        if api.target == 'time' and api.method == 'delta':
            return Call('Time', 'delta', [])

        # Transform.rotate - needs Vec4 axis + angle handling
        if api.target == 'transform' and api.method == 'rotate':
            vec_var = groups.get('vec', '')
            angle_var = groups.get('angle', '')

            # Get Vec3 components from tracked Vec4 values
            vec3 = self.vec4_values.get(vec_var, Vec3(
                Literal(0, 'float'), Literal(0, 'float'), Literal(0, 'float')
            ))
            angle = self.expr_parser.resolve_value(angle_var)

            # Transform.rotate in Iron uses a Vec4 axis and angle
            # We convert to our it_rotate(x, y, z) format
            args = [
                self._multiply_if_nonzero(vec3.x, angle),
                self._multiply_if_nonzero(vec3.y, angle),
                self._multiply_if_nonzero(vec3.z, angle),
            ]
            return Call('transform', 'rotate', args)

        # Transform.translate - needs Vec4 handling
        if api.target == 'transform' and api.method == 'translate':
            vec_var = groups.get('vec', '')
            vec3 = self.vec4_values.get(vec_var, Vec3(
                Literal(0, 'float'), Literal(0, 'float'), Literal(0, 'float')
            ))
            return Call('transform', 'translate', [vec3.x, vec3.y, vec3.z])

        # Scene.setActive - needs scene name resolution
        if api.target == 'scene' and api.method == 'setactive':
            scene_var = groups.get('scene', '')

            # First check if register has been reassigned
            if scene_var.startswith('r') and self.registers.get(scene_var):
                scene_expr = self.registers.get(scene_var)
                return Call('Scene', 'setActive', [scene_expr])

            # Then check if it's a string constant from setup code
            scene_name = self.string_consts.get(scene_var)
            if scene_name:
                return Call('Scene', 'setActive', [Literal(scene_name, 'string')])

            # Fall back to resolving as an expression
            scene_expr = self.expr_parser.resolve_value(scene_var)
            return Call('Scene', 'setActive', [scene_expr])

        # Vec4.new - internal tracking only
        if api.target == 'internal' and api.method == 'vec4_new':
            # This is handled separately in _collect_constants
            return None

        return None

    def _multiply_if_nonzero(self, axis_component: Expr, angle: Expr) -> Expr:
        """Multiply axis component by angle, simplifying if component is 0 or 1."""
        if isinstance(axis_component, Literal):
            if axis_component.value == 0:
                return Literal(0.0, 'float')
            elif axis_component.value == 1:
                return angle
        return BinaryOp('*', axis_component, angle)


# =============================================================================
# Trait Parser
# =============================================================================

class TraitParser:
    """Parses complete HLC trait files into TraitAST nodes."""

    def __init__(self):
        self.func_parser = FunctionParser()

    def parse_trait(self, header_path: str, source_path: str) -> TraitAST:
        """Parse a trait from its header and source files."""
        with open(header_path, 'r', encoding='utf-8') as f:
            header_content = f.read()
        with open(source_path, 'r', encoding='utf-8') as f:
            source_content = f.read()

        # Extract trait name from filename
        base_name = os.path.basename(source_path)[:-2]  # Remove .c
        c_name = f'arm__{base_name}'

        trait = TraitAST(base_name, c_name, header_file=header_path, source_file=source_path)

        # Parse struct members from header
        trait.members = self._parse_members(header_content, c_name)

        # Parse member default values from constructor
        member_defaults = self._parse_member_defaults(source_content, base_name)
        for member in trait.members:
            if member.name in member_defaults:
                member.default_value = member_defaults[member.name]

        # Find lifecycle function mappings
        lifecycle_map = self._find_lifecycle_functions(source_content, base_name)

        # Parse each lifecycle function
        for func_name, lifecycle in lifecycle_map.items():
            body = self._extract_function_body(source_content, func_name)
            if body:
                func = self.func_parser.parse_function(body, lifecycle, func_name)
                trait.functions.append(func)

        return trait

    def _parse_members(self, header_content: str, c_name: str) -> List[TraitMember]:
        """Parse struct members from the header file."""
        members = []

        # Find struct definition
        struct_pattern = rf'struct\s+_{c_name}\s*\{{([^}}]+)\}}'
        match = re.search(struct_pattern, header_content, re.DOTALL)
        if not match:
            return members

        struct_body = match.group(1)

        # Parse member declarations
        member_pattern = re.compile(r'^\s*(\w[\w\s\*]*?)\s+(\w+)\s*;', re.MULTILINE)
        for m in member_pattern.finditer(struct_body):
            member_type = m.group(1).strip()
            member_name = m.group(2)

            # Skip HL runtime internals
            if member_name.startswith('$') or member_name.startswith('_'):
                continue
            if member_type in ('hl_type', 'vdynamic', 'varray'):
                continue
            # Skip system members (gamepad, keyboard, etc.)
            if member_name in get_skip_member_names():
                continue
            # Skip Iron/Kha/Armory internal types
            if any(member_type.startswith(prefix) for prefix in get_skip_type_prefixes()):
                continue

            members.append(TraitMember(member_name, member_type))

        return members

    def _parse_member_defaults(self, source_content: str, base_name: str) -> Dict[str, Any]:
        """Parse default member values from the constructor."""
        defaults = {}

        # Find the main constructor: arm_TraitName_new(...)
        func_name = f'arm_{base_name}_new'
        body = self._extract_function_body(source_content, func_name)
        if not body:
            return defaults

        # Find numeric assignments to members
        # Pattern: r0->member = value; or r1 = value; r0->member = r1;

        # First find local values
        local_values = {}
        for match in re.finditer(r'(\w+)\s*=\s*(-?[\d.]+)\s*;', body):
            local_values[match.group(1)] = float(match.group(2))

        # Find member assignments
        for match in re.finditer(r'r0->(\w+)\s*=\s*(\w+)\s*;', body):
            member = match.group(1)
            value_var = match.group(2)
            if value_var in local_values:
                defaults[member] = local_values[value_var]

        # Direct assignments
        for match in re.finditer(r'r0->(\w+)\s*=\s*(-?[\d.]+)\s*;', body):
            defaults[match.group(1)] = float(match.group(2))

        return defaults

    def _find_lifecycle_functions(self, source_content: str, base_name: str) -> Dict[str, str]:
        """Find which functions are registered for each lifecycle."""
        lifecycle_map = {}

        # Pattern: hl_alloc_closure_ptr(..., func_name, ...); iron_Trait_notifyOnXxx(...);
        # They're usually on consecutive lines

        closure_pattern = re.compile(
            r'hl_alloc_closure_ptr\s*\([^,]+,\s*(arm_' + base_name + r'_new(?:__[$]\d+)?)\s*,[^)]+\)\s*;'
            r'\s*iron_Trait_notifyOn(\w+)',
            re.DOTALL
        )

        for match in closure_pattern.finditer(source_content):
            func_name = match.group(1)
            lifecycle = match.group(2).lower()
            lifecycle_map[func_name] = lifecycle

        # Also check for static closures
        static_pattern = re.compile(
            r'static\s+vclosure\s+(\w+)\s*=\s*\{[^,]+,\s*(arm_' + base_name + r'_new(?:__[$]\d+)?)\s*,'
        )
        notify_pattern = re.compile(r'iron_Trait_notifyOn(\w+)\s*\([^,]+,\s*&(\w+)\s*\)')

        static_closures = {m.group(1): m.group(2) for m in static_pattern.finditer(source_content)}
        for match in notify_pattern.finditer(source_content):
            lifecycle = match.group(1).lower()
            closure_var = match.group(2)
            if closure_var in static_closures:
                func_name = static_closures[closure_var]
                lifecycle_map[func_name] = lifecycle

        return lifecycle_map

    def _extract_function_body(self, content: str, func_name: str) -> Optional[str]:
        """Extract the body of a C function."""
        pattern = rf'void\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{'
        match = re.search(pattern, content)
        if not match:
            return None

        start = match.end() - 1
        depth = 1
        pos = start + 1

        while pos < len(content) and depth > 0:
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
            pos += 1

        return content[start:pos]


# =============================================================================
# Public API
# =============================================================================

def parse_trait_file(header_path: str, source_path: str) -> TraitAST:
    """Parse a trait from its HLC files into an AST."""
    parser = TraitParser()
    return parser.parse_trait(header_path, source_path)


def parse_all_traits(hlc_path: str) -> Dict[str, TraitAST]:
    """
    Parse all traits in the HLC build directory.

    Returns:
        Dict mapping trait name to TraitAST
    """
    arm_dir = os.path.join(hlc_path, 'arm')
    if not os.path.isdir(arm_dir):
        log.warn(f"No arm/ directory found in {hlc_path}")
        return {}

    traits = {}

    for filename in os.listdir(arm_dir):
        if filename.endswith('.c'):
            base = filename[:-2]
            header = os.path.join(arm_dir, f'{base}.h')
            source = os.path.join(arm_dir, filename)

            if os.path.isfile(header):
                try:
                    trait = parse_trait_file(header, source)
                    traits[trait.name] = trait
                    log.info(f"  Parsed trait '{trait.name}':")
                    log.info(f"    Members: {[m.name for m in trait.members]}")
                    log.info(f"    Functions: {[f.lifecycle for f in trait.functions]}")
                except Exception as e:
                    log.warn(f"Failed to parse trait {base}: {e}")

    return traits
