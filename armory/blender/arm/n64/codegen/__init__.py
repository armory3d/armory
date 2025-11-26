"""
N64 Code Generation Module

Generates N64 C code from parsed HLC AST.
"""

from . import generator

from .generator import (
    TraitCodeGenerator,
    ExpressionGenerator,
    StatementGenerator,
    ast_to_summary,
    scan_and_summarize,
    parse_all_traits,
    write_traits_files,
)

__all__ = [
    'generator',
    'TraitCodeGenerator',
    'ExpressionGenerator',
    'StatementGenerator',
    'ast_to_summary',
    'scan_and_summarize',
    'parse_all_traits',
    'write_traits_files',
]
