"""
N64 Trait Utilities

Shared utilities for trait data extraction and filtering.
Used by both exporter.py and trait_generator.py.
"""

# Types/prefixes to skip (Iron runtime internals, not user data)
SKIP_TYPE_PREFIXES = (
    'iron__',
    'kha__',
    'armory__',
    'hl_',
    'vdynamic',
    'varray',
)

SKIP_MEMBER_NAMES = (
    'object',
    'transform',
    'gamepad',
    'keyboard',
    'mouse',
    'name',
)

# Only primitive types supported for N64 trait data
SUPPORTED_TYPES = ('double', 'float', 'int', 'bool')

# Map HLC C types to N64 C types
HLC_TYPE_MAP = {
    'double': 'float',
    'float': 'float',
    'int': 'int32_t',
    'bool': 'bool',
}


def is_supported_member(member_name: str, member_type: str) -> bool:
    """Check if a trait member should be included in the data struct."""
    if member_name.startswith('_') or member_name.startswith('$'):
        return False
    if member_name in SKIP_MEMBER_NAMES:
        return False
    if any(member_type.startswith(prefix) for prefix in SKIP_TYPE_PREFIXES):
        return False
    if member_type not in SUPPORTED_TYPES:
        return False
    return True


def filter_trait_members(members: dict) -> dict:
    """Filter trait members to only supported primitives."""
    return {k: v for k, v in members.items() if is_supported_member(k, v)}


def extract_blender_trait_props(trait) -> dict:
    """
    Extract per-instance property values from a Blender trait.

    Args:
        trait: A Blender ArmTraitListItem

    Returns:
        Dict of {prop_name: value} for supported types
    """
    props = {}
    if hasattr(trait, 'arm_traitpropslist'):
        for prop in trait.arm_traitpropslist:
            if prop.type == 'Float':
                props[prop.name] = prop.value_float
            elif prop.type == 'Int':
                props[prop.name] = prop.value_int
            elif prop.type == 'Bool':
                props[prop.name] = prop.value_bool
    return props
