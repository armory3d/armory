"""
HLC AST Node Definitions

Abstract Syntax Tree nodes for representing parsed HashLink C code.
These nodes capture the structure and semantics of trait functions,
enabling accurate translation to N64 C code.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Any


# =============================================================================
# Expression Nodes
# =============================================================================

@dataclass
class Literal:
    """A literal value (number, string, boolean)."""
    value: Any
    type: str  # 'int', 'float', 'double', 'string', 'bool'

    def __repr__(self):
        if self.type == 'string':
            return f'Literal("{self.value}")'
        return f'Literal({self.value})'


@dataclass
class MemberAccess:
    """
    Access a member of an object.

    Examples:
        r0->speed       -> MemberAccess('self', 'speed')
        r7->transform   -> MemberAccess('object', 'transform')
    """
    object: str   # 'self' for trait instance, or resolved object type
    member: str   # Member name

    def __repr__(self):
        return f'{self.object}.{self.member}'


@dataclass
class Variable:
    """A local variable reference."""
    name: str

    def __repr__(self):
        return f'Var({self.name})'


@dataclass
class BinaryOp:
    """
    Binary operation between two expressions.

    Examples:
        speed * delta   -> BinaryOp('*', MemberAccess('self', 'speed'), Call(...))
        health > 0      -> BinaryOp('>', MemberAccess('self', 'health'), Literal(0))
    """
    op: str       # '*', '+', '-', '/', '==', '!=', '>', '<', '>=', '<=', '&&', '||'
    left: 'Expr'
    right: 'Expr'

    def __repr__(self):
        return f'({self.left} {self.op} {self.right})'


@dataclass
class UnaryOp:
    """Unary operation on an expression."""
    op: str       # '!', '-', '++'
    operand: 'Expr'

    def __repr__(self):
        return f'({self.op}{self.operand})'


@dataclass
class Call:
    """
    A function/method call.

    Examples:
        gamepad.down("a")           -> Call('gamepad', 'down', [Literal("a")])
        transform.rotate(v, angle)  -> Call('transform', 'rotate', [v, angle])
        Time.delta                  -> Call('Time', 'delta', [])
        Scene.setActive("Level_02") -> Call('Scene', 'setActive', [Literal("Level_02")])
    """
    target: str        # 'gamepad', 'transform', 'Time', 'Scene', etc.
    method: str        # 'down', 'rotate', 'delta', 'setActive', etc.
    args: List['Expr'] = field(default_factory=list)

    def __repr__(self):
        args_str = ', '.join(repr(a) for a in self.args)
        return f'{self.target}.{self.method}({args_str})'


@dataclass
class Vec3:
    """
    A 3D vector (extracted from Vec4 construction).

    Used for transform operations that take x, y, z components.
    """
    x: 'Expr'
    y: 'Expr'
    z: 'Expr'

    def __repr__(self):
        return f'Vec3({self.x}, {self.y}, {self.z})'


@dataclass
class Cast:
    """Type cast expression."""
    target_type: str
    expr: 'Expr'

    def __repr__(self):
        return f'({self.target_type}){self.expr}'


# Union type for all expressions
Expr = Union[Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast]


# =============================================================================
# Statement Nodes
# =============================================================================

@dataclass
class ExprStmt:
    """An expression used as a statement (typically a call)."""
    expr: Expr

    def __repr__(self):
        return f'{self.expr};'


@dataclass
class Assignment:
    """
    Assignment to a variable or member.

    Examples:
        speed = 5.0                -> Assignment(MemberAccess('self', 'speed'), Literal(5.0))
        score = score + 10         -> Assignment(MemberAccess('self', 'score'), BinaryOp(...))
    """
    target: Union[MemberAccess, Variable]
    value: Expr

    def __repr__(self):
        return f'{self.target} = {self.value};'


@dataclass
class IfStmt:
    """
    Conditional statement.

    In HLC, these appear as:
        if( condition ) goto label;
        ... then body ...
        label:

    We invert this to normal if/else structure.
    """
    condition: Expr
    then_body: List['Stmt']
    else_body: Optional[List['Stmt']] = None

    def __repr__(self):
        then_str = '\n  '.join(repr(s) for s in self.then_body)
        if self.else_body:
            else_str = '\n  '.join(repr(s) for s in self.else_body)
            return f'if ({self.condition}) {{\n  {then_str}\n}} else {{\n  {else_str}\n}}'
        return f'if ({self.condition}) {{\n  {then_str}\n}}'


@dataclass
class WhileStmt:
    """While loop (for future support)."""
    condition: Expr
    body: List['Stmt']


@dataclass
class ReturnStmt:
    """Return statement."""
    value: Optional[Expr] = None

    def __repr__(self):
        if self.value:
            return f'return {self.value};'
        return 'return;'


# Union type for all statements
Stmt = Union[ExprStmt, Assignment, IfStmt, WhileStmt, ReturnStmt]


# =============================================================================
# Top-Level Nodes
# =============================================================================

@dataclass
class TraitFunction:
    """
    A trait lifecycle function (init, update, remove, add).

    Contains the parsed AST of the function body.
    """
    name: str              # Original HLC function name
    lifecycle: str         # 'init', 'update', 'remove', 'add', 'constructor'
    statements: List[Stmt] = field(default_factory=list)

    # Metadata extracted during parsing
    uses_delta: bool = False       # Uses Time.delta
    uses_transform: bool = False   # Uses transform operations
    uses_input: bool = False       # Uses input (gamepad/keyboard/mouse)
    uses_scene: bool = False       # Uses scene switching

    def __repr__(self):
        stmts = '\n  '.join(repr(s) for s in self.statements)
        return f'TraitFunction({self.lifecycle}) {{\n  {stmts}\n}}'


@dataclass
class TraitMember:
    """A member variable of a trait."""
    name: str
    type: str              # HLC type (double, float, int, bool, String, etc.)
    default_value: Optional[Any] = None

    def __repr__(self):
        if self.default_value is not None:
            return f'{self.type} {self.name} = {self.default_value}'
        return f'{self.type} {self.name}'


@dataclass
class TraitAST:
    """
    Complete AST for a parsed trait.

    This is the top-level node containing all information needed
    to generate N64 C code for a trait.
    """
    name: str                              # Trait class name (e.g., "Rotator")
    c_name: str                            # HLC C name (e.g., "arm__Rotator")
    members: List[TraitMember] = field(default_factory=list)
    functions: List[TraitFunction] = field(default_factory=list)

    # Source file info
    header_file: str = ""
    source_file: str = ""

    def get_function(self, lifecycle: str) -> Optional[TraitFunction]:
        """Get a function by lifecycle type."""
        for func in self.functions:
            if func.lifecycle == lifecycle:
                return func
        return None

    def get_member(self, name: str) -> Optional[TraitMember]:
        """Get a member by name."""
        for member in self.members:
            if member.name == name:
                return member
        return None

    def __repr__(self):
        members_str = ', '.join(repr(m) for m in self.members)
        funcs_str = '\n'.join(repr(f) for f in self.functions)
        return f'Trait {self.name} {{\n  members: [{members_str}]\n  {funcs_str}\n}}'


# =============================================================================
# Helper Functions
# =============================================================================

def is_numeric_type(type_str: str) -> bool:
    """Check if a type is numeric."""
    return type_str in ('int', 'float', 'double', 'int32_t', 'uint32_t', 'int64_t')


def is_supported_type(type_str: str) -> bool:
    """Check if a type is supported for N64 trait data."""
    return type_str in ('int', 'float', 'double', 'bool')


def literal_from_value(value: Any) -> Literal:
    """Create a Literal node from a Python value."""
    if isinstance(value, bool):
        return Literal(value, 'bool')
    elif isinstance(value, int):
        return Literal(value, 'int')
    elif isinstance(value, float):
        return Literal(value, 'double')
    elif isinstance(value, str):
        return Literal(value, 'string')
    else:
        return Literal(value, 'unknown')


def make_call(target: str, method: str, *args: Expr) -> Call:
    """Helper to create a Call node."""
    return Call(target, method, list(args))


def make_binary(op: str, left: Expr, right: Expr) -> BinaryOp:
    """Helper to create a BinaryOp node."""
    return BinaryOp(op, left, right)


def make_if(condition: Expr, then_body: List[Stmt], else_body: List[Stmt] = None) -> IfStmt:
    """Helper to create an IfStmt node."""
    return IfStmt(condition, then_body, else_body)
