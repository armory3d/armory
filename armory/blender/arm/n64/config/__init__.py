"""
N64 Configuration Module

Loads and provides access to API mappings and input configurations.
"""

from .loader import (
    get_config,
    reload_config,
    get_button_mapping,
    get_input_state_func,
    get_hlc_type_mapping,
    get_skip_member_names,
    get_skip_type_prefixes,
    get_supported_types,
    ApiConfig,
    ApiDefinition,
    CodegenApiDef,
)

__all__ = [
    'get_config',
    'reload_config',
    'get_button_mapping',
    'get_input_state_func',
    'get_hlc_type_mapping',
    'get_skip_member_names',
    'get_skip_type_prefixes',
    'get_supported_types',
    'ApiConfig',
    'ApiDefinition',
    'CodegenApiDef',
]
