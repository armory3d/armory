"""
N64 Utilities Module

Shared utilities for trait filtering and Blender operations.
"""

from .traits import (
    is_supported_member,
    filter_trait_members,
    get_n64_type,
    extract_blender_trait_props,
)

from .blender import (
    copy_src,
    get_clear_color,
    deselect_from_all_viewlayers,
    to_uint8,
)

__all__ = [
    # Trait utilities
    'is_supported_member',
    'filter_trait_members',
    'get_n64_type',
    'extract_blender_trait_props',
    # Blender utilities
    'copy_src',
    'get_clear_color',
    'deselect_from_all_viewlayers',
    'to_uint8',
]
