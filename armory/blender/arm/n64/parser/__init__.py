"""
N64 HLC Parser Module

Parses HashLink C output into AST nodes for translation to N64 C code.
"""

from .ast import (
    Literal, MemberAccess, Variable, BinaryOp, UnaryOp, Call, Vec3, Cast,
    ExprStmt, Assignment, IfStmt, WhileStmt, ReturnStmt,
    TraitMember, TraitFunction, TraitAST,
    Expr, Stmt,
    literal_from_value, make_call, make_binary, make_if,
    is_numeric_type, is_supported_type,
)

from .hlc_parser import (
    TraitParser,
    FunctionParser,
    ExpressionParser,
    parse_all_traits,
)

__all__ = [
    # AST nodes
    'Literal', 'MemberAccess', 'Variable', 'BinaryOp', 'UnaryOp', 'Call', 'Vec3', 'Cast',
    'ExprStmt', 'Assignment', 'IfStmt', 'WhileStmt', 'ReturnStmt',
    'TraitMember', 'TraitFunction', 'TraitAST',
    'Expr', 'Stmt',
    # AST helpers
    'literal_from_value', 'make_call', 'make_binary', 'make_if',
    'is_numeric_type', 'is_supported_type',
    # Parsers
    'TraitParser', 'FunctionParser', 'ExpressionParser', 'parse_all_traits',
]
