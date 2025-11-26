"""
N64 Trait Utilities

Shared utilities for trait data extraction and filtering.
Used by exporter.py and code_generator.py.

All filter lists and type maps are loaded from api_mappings.json via config.loader.
"""

# Lazy-loaded config reference
_config = None


def _get_config():
    """Get config, loading lazily to avoid circular imports."""
    global _config
    if _config is None:
        try:
            from ..config import get_config
        except ImportError:
            from config import get_config
        _config = get_config()
    return _config


# =============================================================================
# Utility Functions
# =============================================================================

def is_supported_member(member_name: str, member_type: str) -> bool:
    """Check if a trait member should be included in the data struct."""
    config = _get_config()

    if member_name.startswith('_') or member_name.startswith('$'):
        return False
    if config.should_skip_member(member_name):
        return False
    if config.should_skip_type(member_type):
        return False
    if not config.is_supported_type(member_type):
        return False
    return True


def filter_trait_members(members: dict) -> dict:
    """Filter trait members to only supported primitives."""
    return {k: v for k, v in members.items() if is_supported_member(k, v)}


def get_n64_type(hlc_type: str) -> str:
    """Map HLC type to N64 C type."""
    return _get_config().map_type('hlc_to_n64', hlc_type)


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
