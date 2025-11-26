"""
N64 Code Generator

Walks the HLC AST and generates N64 C code for libdragon/Tiny3D.
This is the Phase 3 component of the AST-based trait translation pipeline.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
import re

# Try to import arm module (available when running inside Blender)
try:
    import arm
    import arm.utils
    import arm.log as log
    from arm.n64.hlc_ast import (
        Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast, Expr,
        ExprStmt, Assignment, IfStmt, WhileStmt, ReturnStmt, Stmt,
        TraitFunction, TraitMember, TraitAST
    )
    from arm.n64.input_mapping import GAMEPAD_TO_N64_MAP, INPUT_STATE_MAP, SCENE_METHOD_MAP
    from arm.n64.trait_utils import is_supported_member, HLC_TYPE_MAP
    HAS_ARM = True
except ImportError:
    HAS_ARM = False
    # Stub for standalone testing
    class LogStub:
        @staticmethod
        def warn(msg): print(f'WARN: {msg}')
        @staticmethod
        def info(msg): print(f'INFO: {msg}')
    log = LogStub()
    # Import from local modules when arm is not available
    from hlc_ast import (
        Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast, Expr,
        ExprStmt, Assignment, IfStmt, WhileStmt, ReturnStmt, Stmt,
        TraitFunction, TraitMember, TraitAST
    )
    from input_mapping import GAMEPAD_TO_N64_MAP, INPUT_STATE_MAP, SCENE_METHOD_MAP
    from trait_utils import is_supported_member, HLC_TYPE_MAP

if HAS_ARM:
    if arm.is_reload(__name__):
        arm.utils = arm.reload_module(arm.utils)
        log = arm.reload_module(log)
    else:
        arm.enable_reload(__name__)


def safesrc(name: str) -> str:
    """Make a string safe for use as a C identifier."""
    if HAS_ARM:
        return arm.utils.safesrc(name)
    # Standalone implementation
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


# =============================================================================
# Code Generation Context
# =============================================================================

@dataclass
class GeneratorContext:
    """Context passed during code generation."""
    trait_name: str          # e.g., "Rotator"
    func_name: str           # e.g., "rotator" (lowercased, safe C name)
    indent: int = 0          # Current indentation level
    needs_obj: bool = False  # Whether we need ArmObject *obj
    needs_data: bool = False # Whether we need trait data struct access
    has_dt: bool = False     # Whether dt parameter is used

    def indent_str(self) -> str:
        return '    ' * self.indent


# =============================================================================
# Expression Generator
# =============================================================================

class ExpressionGenerator:
    """Generates C code for AST expressions."""

    def __init__(self, ctx: GeneratorContext):
        self.ctx = ctx

    def generate(self, expr: Expr) -> str:
        """Generate C code for an expression."""
        if isinstance(expr, Literal):
            return self._gen_literal(expr)
        elif isinstance(expr, MemberAccess):
            return self._gen_member_access(expr)
        elif isinstance(expr, Variable):
            return self._gen_variable(expr)
        elif isinstance(expr, BinaryOp):
            return self._gen_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            return self._gen_unary_op(expr)
        elif isinstance(expr, Call):
            return self._gen_call(expr)
        elif isinstance(expr, Vec3):
            return self._gen_vec3(expr)
        elif isinstance(expr, Cast):
            return self._gen_cast(expr)
        else:
            log.warn(f'Unknown expression type: {type(expr)}')
            return f'/* unknown: {expr!r} */'

    def _gen_literal(self, lit: Literal) -> str:
        if lit.type == 'string':
            return f'"{lit.value}"'
        elif lit.type == 'float':
            val = lit.value
            # Ensure float suffix
            if isinstance(val, float):
                return f'{val}f'
            return f'{val}.0f'
        elif lit.type == 'bool':
            return 'true' if lit.value else 'false'
        else:
            return str(lit.value)

    def _gen_member_access(self, ma: MemberAccess) -> str:
        if ma.object == 'self':
            # Access trait data member
            self.ctx.needs_data = True
            return f'tdata->{ma.member}'
        else:
            # Access object property (like transform)
            self.ctx.needs_obj = True
            return f'obj->{ma.member}'

    def _gen_variable(self, var: Variable) -> str:
        return var.name

    def _gen_binary_op(self, op: BinaryOp) -> str:
        left = self.generate(op.left)
        right = self.generate(op.right)
        return f'({left} {op.op} {right})'

    def _gen_unary_op(self, op: UnaryOp) -> str:
        operand = self.generate(op.operand)
        return f'({op.op}{operand})'

    def _gen_call(self, call: Call) -> str:
        """Generate code for API calls."""
        target = call.target.lower()
        method = call.method.lower()

        # Time.delta() -> dt (parameter)
        if target == 'time' and method == 'delta':
            self.ctx.has_dt = True
            return 'dt'

        # Gamepad input calls
        if target == 'gamepad':
            return self._gen_gamepad_call(call)

        # Transform calls
        if target == 'transform':
            return self._gen_transform_call(call)

        # Scene calls
        if target == 'scene':
            return self._gen_scene_call(call)

        log.warn(f'Unknown call: {call.target}.{call.method}')
        return f'/* unknown: {call!r} */'

    def _gen_gamepad_call(self, call: Call) -> str:
        """Generate gamepad input check."""
        method = call.method.lower()

        # Get button from first argument
        button = 'a'  # default
        if call.args:
            arg = call.args[0]
            if isinstance(arg, Literal) and arg.type == 'string':
                button = arg.value

        n64_button = GAMEPAD_TO_N64_MAP.get(button.lower(), 'N64_BTN_A')
        n64_func = INPUT_STATE_MAP.get(method, 'input_down')

        return f'{n64_func}({n64_button})'

    def _gen_transform_call(self, call: Call) -> str:
        """Generate transform operation call."""
        self.ctx.needs_obj = True
        method = call.method.lower()

        if method == 'rotate':
            # Args should be (x, y, z) rotation amounts
            if len(call.args) >= 3:
                x = self.generate(call.args[0])
                y = self.generate(call.args[1])
                z = self.generate(call.args[2])
                return f'it_rotate(&obj->transform, {x}, {y}, {z})'
            elif len(call.args) == 1:
                # Single angle - assume Y axis
                angle = self.generate(call.args[0])
                return f'it_rotate(&obj->transform, 0.0f, {angle}, 0.0f)'

        elif method == 'translate':
            if len(call.args) >= 3:
                x = self.generate(call.args[0])
                y = self.generate(call.args[1])
                z = self.generate(call.args[2])
                return f'it_translate(&obj->transform, {x}, {y}, {z})'
            elif len(call.args) == 1:
                # Single value - assume Z axis (forward)
                dist = self.generate(call.args[0])
                return f'it_translate(&obj->transform, 0.0f, 0.0f, {dist})'

        elif method == 'move':
            # move is similar to translate
            if len(call.args) >= 3:
                x = self.generate(call.args[0])
                y = self.generate(call.args[1])
                z = self.generate(call.args[2])
                return f'it_translate(&obj->transform, {x}, {y}, {z})'

        log.warn(f'Unknown transform method: {method}')
        return f'/* unknown transform: {call!r} */'

    def _gen_scene_call(self, call: Call) -> str:
        """Generate scene management call."""
        method = call.method.lower()

        if method == 'setactive':
            # Get scene name from argument
            if call.args:
                arg = call.args[0]
                if isinstance(arg, Literal) and arg.type == 'string':
                    # Direct scene name
                    scene_name = arg.value
                    scene_id = f'SCENE_{safesrc(scene_name).upper()}'
                    return f'scene_switch_to({scene_id})'
                elif isinstance(arg, MemberAccess):
                    # Scene from member variable
                    self.ctx.needs_data = True
                    return f'scene_switch_to(tdata->target_scene)'

        log.warn(f'Unknown scene method: {method}')
        return f'/* unknown scene: {call!r} */'

    def _gen_vec3(self, vec: Vec3) -> str:
        x = self.generate(vec.x)
        y = self.generate(vec.y)
        z = self.generate(vec.z)
        return f'({x}, {y}, {z})'

    def _gen_cast(self, cast: Cast) -> str:
        expr = self.generate(cast.expr)
        return f'({cast.target_type}){expr}'


# =============================================================================
# Statement Generator
# =============================================================================

class StatementGenerator:
    """Generates C code for AST statements."""

    def __init__(self, ctx: GeneratorContext):
        self.ctx = ctx
        self.expr_gen = ExpressionGenerator(ctx)

    def generate(self, stmt: Stmt) -> List[str]:
        """Generate C code lines for a statement."""
        if isinstance(stmt, ExprStmt):
            return self._gen_expr_stmt(stmt)
        elif isinstance(stmt, Assignment):
            return self._gen_assignment(stmt)
        elif isinstance(stmt, IfStmt):
            return self._gen_if_stmt(stmt)
        elif isinstance(stmt, WhileStmt):
            return self._gen_while_stmt(stmt)
        elif isinstance(stmt, ReturnStmt):
            return self._gen_return_stmt(stmt)
        else:
            log.warn(f'Unknown statement type: {type(stmt)}')
            return [f'{self.ctx.indent_str()}/* unknown: {stmt!r} */']

    def _gen_expr_stmt(self, stmt: ExprStmt) -> List[str]:
        """Generate an expression statement (typically a call)."""
        indent = self.ctx.indent_str()
        expr_code = self.expr_gen.generate(stmt.expr)

        # Check if this is a call that should be a statement
        if isinstance(stmt.expr, Call):
            target = stmt.expr.target.lower()
            method = stmt.expr.method.lower()

            # Transform calls are statements
            if target == 'transform':
                return [f'{indent}{expr_code};']

            # Scene calls are statements
            if target == 'scene':
                return [f'{indent}{expr_code};']

        return [f'{indent}{expr_code};']

    def _gen_assignment(self, stmt: Assignment) -> List[str]:
        """Generate an assignment statement."""
        indent = self.ctx.indent_str()
        target = self.expr_gen.generate(stmt.target)
        value = self.expr_gen.generate(stmt.value)
        return [f'{indent}{target} = {value};']

    def _gen_if_stmt(self, stmt: IfStmt) -> List[str]:
        """Generate an if statement."""
        indent = self.ctx.indent_str()
        lines = []

        # Generate condition
        cond = self.expr_gen.generate(stmt.condition)
        lines.append(f'{indent}if ({cond}) {{')

        # Generate then body
        self.ctx.indent += 1
        for s in stmt.then_body:
            lines.extend(self.generate(s))
        self.ctx.indent -= 1

        # Generate else body if present
        if stmt.else_body:
            lines.append(f'{indent}}} else {{')
            self.ctx.indent += 1
            for s in stmt.else_body:
                lines.extend(self.generate(s))
            self.ctx.indent -= 1

        lines.append(f'{indent}}}')
        return lines

    def _gen_while_stmt(self, stmt: WhileStmt) -> List[str]:
        """Generate a while loop."""
        indent = self.ctx.indent_str()
        lines = []

        cond = self.expr_gen.generate(stmt.condition)
        lines.append(f'{indent}while ({cond}) {{')

        self.ctx.indent += 1
        for s in stmt.body:
            lines.extend(self.generate(s))
        self.ctx.indent -= 1

        lines.append(f'{indent}}}')
        return lines

    def _gen_return_stmt(self, stmt: ReturnStmt) -> List[str]:
        """Generate a return statement."""
        indent = self.ctx.indent_str()
        if stmt.value:
            val = self.expr_gen.generate(stmt.value)
            return [f'{indent}return {val};']
        return [f'{indent}return;']


# =============================================================================
# Trait Generator
# =============================================================================

class TraitCodeGenerator:
    """Generates complete N64 C code for a trait from its AST."""

    def __init__(self, trait_ast: TraitAST, scene_map: Dict[str, str] = None):
        """
        Initialize the generator.

        Args:
            trait_ast: The parsed trait AST
            scene_map: Maps scene names to scene IDs (for validation)
        """
        self.ast = trait_ast
        self.scene_map = scene_map or {}
        self.func_name = safesrc(trait_ast.name).lower()

    def generate_data_struct(self) -> str:
        """Generate the trait data struct definition."""
        fields = []

        # Check if any function uses scene switching with member variable
        needs_scene_field = False
        for func in self.ast.functions:
            for stmt in func.statements:
                if self._stmt_uses_scene_member(stmt):
                    needs_scene_field = True
                    break

        if needs_scene_field:
            fields.append('    SceneId target_scene;')

        # Add supported member variables
        for member in self.ast.members:
            if is_supported_member(member.name, member.type):
                c_type = HLC_TYPE_MAP.get(member.type, 'float')
                fields.append(f'    {c_type} {member.name};')

        if not fields:
            return ''

        struct_name = f'{self.ast.name}Data'
        return f'typedef struct {{\n' + '\n'.join(fields) + f'\n}} {struct_name};\n'

    def _stmt_uses_scene_member(self, stmt: Stmt) -> bool:
        """Check if a statement uses Scene.setActive with a member variable."""
        if isinstance(stmt, ExprStmt):
            if isinstance(stmt.expr, Call):
                if stmt.expr.target.lower() == 'scene' and stmt.expr.method.lower() == 'setactive':
                    if stmt.expr.args and isinstance(stmt.expr.args[0], MemberAccess):
                        return True
        elif isinstance(stmt, IfStmt):
            for s in stmt.then_body:
                if self._stmt_uses_scene_member(s):
                    return True
            if stmt.else_body:
                for s in stmt.else_body:
                    if self._stmt_uses_scene_member(s):
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
        """Generate the complete trait implementation."""
        lines = [f'// Trait: {self.ast.name}']

        # Generate on_ready (init)
        init_func = self.ast.get_function('init')
        lines.extend(self._gen_lifecycle_function('on_ready', init_func, has_dt=False))
        lines.append('')

        # Generate on_update
        update_func = self.ast.get_function('update')
        lines.extend(self._gen_lifecycle_function('on_update', update_func, has_dt=True))
        lines.append('')

        # Generate on_remove
        remove_func = self.ast.get_function('remove')
        lines.extend(self._gen_lifecycle_function('on_remove', remove_func, has_dt=False))
        lines.append('')

        return '\n'.join(lines)

    def _gen_lifecycle_function(self, lifecycle_name: str, func: Optional[TraitFunction], has_dt: bool) -> List[str]:
        """Generate a lifecycle function implementation."""
        if has_dt:
            sig = f'void {self.func_name}_{lifecycle_name}(void *entity, float dt, void *data)'
        else:
            sig = f'void {self.func_name}_{lifecycle_name}(void *entity, void *data)'

        lines = [f'{sig} {{']

        # Create context for code generation
        ctx = GeneratorContext(
            trait_name=self.ast.name,
            func_name=self.func_name,
            indent=1
        )

        # Generate body statements
        body_lines = []
        if func and func.statements:
            stmt_gen = StatementGenerator(ctx)
            for stmt in func.statements:
                body_lines.extend(stmt_gen.generate(stmt))

        # Add variable declarations based on what was used
        decl_lines = []
        if ctx.needs_obj:
            decl_lines.append('    ArmObject *obj = (ArmObject *)entity;')
        else:
            decl_lines.append('    (void)entity;')

        if has_dt:
            if not ctx.has_dt:
                decl_lines.append('    (void)dt;')

        if ctx.needs_data:
            decl_lines.append(f'    {self.ast.name}Data *tdata = ({self.ast.name}Data *)data;')
        else:
            decl_lines.append('    (void)data;')

        # Combine declarations and body
        lines.extend(decl_lines)
        if body_lines:
            lines.append('')  # Blank line between decls and body
            lines.extend(body_lines)

        lines.append('}')
        return lines


# =============================================================================
# Public API
# =============================================================================

def generate_trait_from_ast(trait_ast: TraitAST, scene_map: Dict[str, str] = None) -> Tuple[str, str, str]:
    """
    Generate N64 C code from a trait AST.

    Args:
        trait_ast: The parsed trait AST
        scene_map: Maps scene names to scene IDs

    Returns:
        Tuple of (declarations, data_struct, implementation)
    """
    gen = TraitCodeGenerator(trait_ast, scene_map)

    declarations = '\n'.join(gen.generate_declarations())
    data_struct = gen.generate_data_struct()
    implementation = gen.generate_implementation()

    return declarations, data_struct, implementation


def generate_all_traits_from_ast(
    trait_asts: List[TraitAST],
    scene_map: Dict[str, str] = None
) -> Tuple[str, str, str]:
    """
    Generate N64 C code for multiple traits from their ASTs.

    Args:
        trait_asts: List of parsed trait ASTs
        scene_map: Maps scene names to scene IDs

    Returns:
        Tuple of (all_declarations, all_data_structs, all_implementations)
    """
    all_decls = []
    all_structs = []
    all_impls = []

    for ast in sorted(trait_asts, key=lambda t: t.name):
        decls, struct, impl = generate_trait_from_ast(ast, scene_map)
        all_decls.append(decls)
        if struct:
            all_structs.append(struct)
        all_impls.append(impl)

    return '\n'.join(all_decls), '\n'.join(all_structs), '\n'.join(all_impls)
