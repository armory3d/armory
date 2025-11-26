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
    from arm.n64.parser import (
        Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast, Expr,
        ExprStmt, Assignment, IfStmt, WhileStmt, ReturnStmt, Stmt,
        TraitFunction, TraitMember, TraitAST
    )
    from arm.n64.config import get_config
    from arm.n64.utils import is_supported_member, get_n64_type
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
    from parser.ast import (
        Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast, Expr,
        ExprStmt, Assignment, IfStmt, WhileStmt, ReturnStmt, Stmt,
        TraitFunction, TraitMember, TraitAST
    )
    from config import get_config
    from utils.traits import is_supported_member, get_n64_type

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
        # Warn if this looks like an unresolved HLC register
        if re.match(r'^r\d+$', var.name):
            log.warn(f'Unresolved HLC register in generated code: {var.name}')
            return f'/* unresolved: {var.name} */ 0'
        return var.name

    def _gen_binary_op(self, op: BinaryOp) -> str:
        left = self.generate(op.left)
        right = self.generate(op.right)
        return f'({left} {op.op} {right})'

    def _gen_unary_op(self, op: UnaryOp) -> str:
        operand = self.generate(op.operand)
        return f'({op.op}{operand})'

    def _gen_call(self, call: Call) -> str:
        """Generate code for API calls using config-driven templates."""
        target = call.target.lower()
        method = call.method.lower()

        # Look up in codegen config
        config = get_config()
        api_def = config.get_codegen_api(target, method)

        if api_def:
            return self._apply_codegen_template(call, api_def)

        log.warn(f'Unknown call: {call.target}.{call.method}')
        return f'/* unknown: {call!r} */'

    def _apply_codegen_template(self, call: Call, api_def) -> str:
        """Apply a codegen template from config.

        Templates use placeholders like {x}, {y}, {z}, {button}, {scene_id}.
        Special handling for variants (1_arg vs 3_arg) and member access.
        """
        # Apply context flags from config
        if api_def.flags.get('needs_obj'):
            self.ctx.needs_obj = True
        if api_def.flags.get('needs_data'):
            self.ctx.needs_data = True
        if api_def.flags.get('has_dt'):
            self.ctx.has_dt = True

        # Check for variants based on argument count or type
        output_template = api_def.output

        if api_def.variants:
            # Check for member_access variant (e.g., scene.setactive with MemberAccess arg)
            if 'member_access' in api_def.variants and call.args:
                if isinstance(call.args[0], MemberAccess):
                    output_template = api_def.variants['member_access']
                    self.ctx.needs_data = True

            # Check for argument count variants
            arg_count = len(call.args)
            variant_key = f'{arg_count}_arg'
            if variant_key in api_def.variants:
                output_template = api_def.variants[variant_key]

        # Build substitution dict from arguments
        subs = self._build_substitutions(call, api_def)

        # Apply template substitutions
        result = output_template
        for key, value in subs.items():
            result = result.replace(f'{{{key}}}', value)

        return result

    def _build_substitutions(self, call: Call, api_def) -> dict:
        """Build substitution dict for template placeholders."""
        subs = {}
        args_spec = api_def.args

        for i, arg in enumerate(call.args):
            # Check if args_spec defines a name for this position
            if i < len(args_spec):
                arg_name = args_spec[i]
            else:
                arg_name = f'arg{i}'

            # Special handling based on argument type
            if isinstance(arg, Literal):
                if arg.type == 'string':
                    # For button mappings, the value is already the N64 constant
                    subs[arg_name] = arg.value
                    # Also add scene_id for scene calls
                    if arg_name == 'scene':
                        scene_name = arg.value
                        subs['scene_id'] = f'SCENE_{safesrc(scene_name).upper()}'
                else:
                    subs[arg_name] = self.generate(arg)
            elif isinstance(arg, MemberAccess):
                subs[arg_name] = self.generate(arg)
            else:
                subs[arg_name] = self.generate(arg)

        return subs

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
                c_type = get_n64_type(member.type)
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


# =============================================================================
# HLC Build Integration
# =============================================================================

def get_hlc_build_path() -> str:
    """Get the path to HashLink C build output."""
    if HAS_ARM:
        build_dir = arm.utils.build_dir()
    else:
        build_dir = '.'

    import os
    possible_paths = [
        os.path.join(build_dir, 'windows-hl-build'),
        os.path.join(build_dir, 'linux-hl-build'),
        os.path.join(build_dir, 'osx-hl-build'),
    ]

    for path in possible_paths:
        if os.path.isdir(path):
            return path

    return possible_paths[0]


def find_trait_files(hlc_path: str) -> List[Tuple[str, str]]:
    """
    Find all trait C/H file pairs in the arm/ directory.

    Returns:
        List of (header_path, source_path) tuples
    """
    import os
    arm_dir = os.path.join(hlc_path, 'arm')
    if not os.path.isdir(arm_dir):
        return []

    trait_files = []

    for filename in os.listdir(arm_dir):
        if filename.endswith('.c'):
            base = filename[:-2]
            source = os.path.join(arm_dir, filename)
            header = os.path.join(arm_dir, f'{base}.h')
            if os.path.exists(header):
                trait_files.append((header, source))

    return trait_files


def parse_all_traits() -> Dict[str, TraitAST]:
    """
    Parse all traits from the HLC build directory.

    Returns:
        Dictionary mapping trait name to TraitAST
    """
    # Import parser here to avoid circular imports
    if HAS_ARM:
        from arm.n64.parser import TraitParser
    else:
        from parser.hlc_parser import TraitParser

    hlc_path = get_hlc_build_path()
    trait_files = find_trait_files(hlc_path)

    parser = TraitParser()
    traits = {}

    for header_path, source_path in trait_files:
        try:
            ast = parser.parse_trait(header_path, source_path)
            if ast.functions:  # Only include traits with actual code
                traits[ast.name] = ast
        except Exception as e:
            log.warn(f'Failed to parse trait {source_path}: {e}')

    return traits


def ast_to_summary(traits: Dict[str, TraitAST]) -> Dict:
    """
    Convert parsed trait ASTs to a summary dictionary.

    Extracts metadata about traits for use by the exporter:
    - Member names and types
    - Input buttons used
    - Transform/scene operations
    """
    summary = {
        'traits': {},
        'input_buttons': set(),
        'has_transform': False,
        'has_scene': False,
        'has_time': False,
        'scene_names': set(),
    }

    for name, ast in traits.items():
        trait_summary = {
            'members': {m.name: m.type for m in ast.members},
            'member_values': {m.name: m.default_value for m in ast.members if m.default_value is not None},
            'functions': {},
            'input_calls': [],
            'transform_calls': [],
            'scene_calls': [],
        }

        for func in ast.functions:
            # Analyze statements to extract call info
            _analyze_statements(func.statements, trait_summary, summary, func.lifecycle)

            trait_summary['functions'][func.lifecycle] = {
                'name': func.name,
            }

        summary['traits'][name] = trait_summary

    # Convert sets to lists
    summary['input_buttons'] = list(summary['input_buttons'])
    summary['scene_names'] = list(summary['scene_names'])

    return summary


def _analyze_statements(statements: List[Stmt], trait_summary: Dict, summary: Dict, lifecycle: str):
    """Recursively analyze statements to extract API call info."""
    for stmt in statements:
        if isinstance(stmt, ExprStmt):
            _analyze_expr(stmt.expr, trait_summary, summary, lifecycle)
        elif isinstance(stmt, IfStmt):
            _analyze_expr(stmt.condition, trait_summary, summary, lifecycle)
            _analyze_statements(stmt.then_body, trait_summary, summary, lifecycle)
            if stmt.else_body:
                _analyze_statements(stmt.else_body, trait_summary, summary, lifecycle)
        elif isinstance(stmt, Assignment):
            _analyze_expr(stmt.value, trait_summary, summary, lifecycle)


def _analyze_expr(expr: Expr, trait_summary: Dict, summary: Dict, lifecycle: str):
    """Analyze an expression for API calls."""
    if isinstance(expr, Call):
        target = expr.target.lower()
        method = expr.method.lower()

        if target == 'gamepad':
            button = 'a'  # default
            if expr.args and isinstance(expr.args[0], Literal):
                button = expr.args[0].value
            trait_summary['input_calls'].append({
                'method': method,
                'button': button,
                'lifecycle': lifecycle,
            })
            summary['input_buttons'].add(button)

        elif target == 'transform':
            trait_summary['transform_calls'].append({
                'method': method,
                'lifecycle': lifecycle,
            })
            summary['has_transform'] = True

        elif target == 'scene':
            scene_name = 'unknown'
            if expr.args:
                arg = expr.args[0]
                if isinstance(arg, Literal) and arg.type == 'string':
                    scene_name = arg.value
                elif isinstance(arg, MemberAccess):
                    scene_name = f'member:{arg.member}'  # Mark as member-based
            trait_summary['scene_calls'].append({
                'method': method,
                'scene_name': scene_name,
                'lifecycle': lifecycle,
            })
            summary['has_scene'] = True
            summary['scene_names'].add(scene_name)

        elif target == 'time' and method == 'delta':
            summary['has_time'] = True

        # Analyze nested expressions in call args
        for arg in expr.args:
            _analyze_expr(arg, trait_summary, summary, lifecycle)

    elif isinstance(expr, BinaryOp):
        _analyze_expr(expr.left, trait_summary, summary, lifecycle)
        _analyze_expr(expr.right, trait_summary, summary, lifecycle)

    elif isinstance(expr, UnaryOp):
        _analyze_expr(expr.operand, trait_summary, summary, lifecycle)


def scan_and_summarize() -> Tuple[Dict[str, TraitAST], Dict]:
    """
    Scan HLC build and return both parsed ASTs and summary.

    Returns:
        Tuple of (trait_asts dict, trait_info summary dict)
    """
    traits = parse_all_traits()
    summary = ast_to_summary(traits)
    return traits, summary


def write_traits_files(
    trait_classes: Set[str],
    trait_asts: Dict[str, TraitAST],
    trait_data_instances: List[Tuple[str, str, str]] = None
):
    """
    Write traits.h and traits.c files using AST-based code generation.

    Args:
        trait_classes: Set of trait class names to generate
        trait_asts: Dictionary of trait name -> TraitAST
        trait_data_instances: List of (var_name, type_name, init_str) tuples
    """
    import os

    if trait_data_instances is None:
        trait_data_instances = []

    # Filter to only requested traits
    asts_to_generate = [trait_asts[name] for name in trait_classes if name in trait_asts]

    # Also generate scaffolds for traits not in AST
    scaffold_traits = trait_classes - set(trait_asts.keys())

    # Generate code from ASTs
    declarations, data_structs, implementations = generate_all_traits_from_ast(asts_to_generate)

    # Generate scaffolds for traits without HLC data
    for trait_class in sorted(scaffold_traits):
        func_name = safesrc(trait_class).lower()
        declarations += f'\nvoid {func_name}_on_ready(void *entity, void *data);'
        declarations += f'\nvoid {func_name}_on_update(void *entity, float dt, void *data);'
        declarations += f'\nvoid {func_name}_on_remove(void *entity, void *data);'

        implementations += f'\n// Trait: {trait_class} (scaffold - no HLC data)\n'
        implementations += f'void {func_name}_on_ready(void *entity, void *data) {{\n'
        implementations += '    (void)entity;\n    (void)data;\n}\n\n'
        implementations += f'void {func_name}_on_update(void *entity, float dt, void *data) {{\n'
        implementations += '    (void)entity;\n    (void)dt;\n    (void)data;\n}\n\n'
        implementations += f'void {func_name}_on_remove(void *entity, void *data) {{\n'
        implementations += '    (void)entity;\n    (void)data;\n}\n'

    # Generate trait data instances
    data_definitions = []
    data_externs = []
    for var_name, type_name, init_str in trait_data_instances:
        data_definitions.append(f'{type_name} {var_name} = {{ {init_str} }};')
        data_externs.append(f'extern {type_name} {var_name};')

    data_definitions_str = '\n'.join(data_definitions)
    data_externs_str = '\n'.join(data_externs)

    if not HAS_ARM:
        log.info(f'Would write traits.h and traits.c')
        log.info(f'Declarations:\n{declarations}')
        log.info(f'Data structs:\n{data_structs}')
        log.info(f'Implementations:\n{implementations}')
        return

    # Write traits.h
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'traits.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.h')
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()
    output = tmpl_content.format(
        trait_data_structs=data_structs,
        trait_declarations=declarations,
        trait_data_externs=data_externs_str
    )
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Write traits.c
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'traits.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.c')
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()
    output = tmpl_content.format(
        trait_implementations=implementations,
        trait_data_definitions=data_definitions_str
    )
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Log what was generated
    if asts_to_generate:
        log.info(f'Generated traits from AST: {", ".join(sorted(a.name for a in asts_to_generate))}')
    if scaffold_traits:
        log.info(f'Generated trait scaffolds: {", ".join(sorted(scaffold_traits))}')
    if trait_data_instances:
        log.info(f'Generated {len(trait_data_instances)} trait data instances')
