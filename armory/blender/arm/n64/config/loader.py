"""
API Loader - Config-driven API mappings for N64 exporter.

Loads configuration files and provides compiled patterns and lookup functions
for the parser and code generator.

Configuration files:
  - api_mappings.json: HLC patterns, type maps, filters
  - input_mappings.json: Button and input state mappings
"""

import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class ApiDefinition:
    """Compiled API definition from config."""
    name: str
    pattern: re.Pattern
    target: str
    method: str
    output: str = ''
    args: List[Dict[str, str]] = field(default_factory=list)
    handler: str = 'template'  # 'template' or 'custom'
    flags: Dict[str, bool] = field(default_factory=dict)


class ApiConfig:
    """Holds loaded and compiled API configuration."""

    def __init__(self):
        self.apis: Dict[str, ApiDefinition] = {}
        self.value_maps: Dict[str, Dict[str, str]] = {}
        self.type_maps: Dict[str, Dict[str, str]] = {}
        self.filters: Dict[str, List[str]] = {}
        self._loaded = False

    def load(self, config_dir: str = None):
        """Load configuration from JSON files."""
        if config_dir is None:
            config_dir = os.path.dirname(__file__)

        # Load main API mappings
        api_path = os.path.join(config_dir, 'api_mappings.json')
        if not os.path.exists(api_path):
            raise FileNotFoundError(f"API config not found: {api_path}")

        with open(api_path, 'r', encoding='utf-8') as f:
            api_config = json.load(f)

        # Load input mappings (separate file for clarity)
        input_path = os.path.join(config_dir, 'input_mappings.json')
        input_config = {}
        if os.path.exists(input_path):
            with open(input_path, 'r', encoding='utf-8') as f:
                input_config = json.load(f)

        self._parse_config(api_config, input_config)
        self._loaded = True

    def _parse_config(self, api_config: dict, input_config: dict):
        """Parse loaded configs into compiled structures."""
        # Parse API definitions
        for name, api_def in api_config.get('apis', {}).items():
            pattern_str = api_def.get('hlc_pattern', '')
            try:
                pattern = re.compile(pattern_str)
            except re.error as e:
                print(f"Warning: Invalid regex for {name}: {e}")
                continue

            self.apis[name] = ApiDefinition(
                name=name,
                pattern=pattern,
                target=api_def.get('target', ''),
                method=api_def.get('method', ''),
                output=api_def.get('output', ''),
                args=api_def.get('args', []),
                handler=api_def.get('handler', 'template'),
                flags=api_def.get('flags', {}),
            )

        # Parse value maps from both configs
        self.value_maps = api_config.get('value_maps', {})
        # Merge input mappings (excluding _comment keys)
        for key, value in input_config.items():
            if not key.startswith('_'):
                self.value_maps[key] = {k: v for k, v in value.items() if not k.startswith('_')}

        # Parse type maps
        self.type_maps = api_config.get('type_maps', {})

        # Parse filters
        self.filters = api_config.get('filters', {})

    def ensure_loaded(self):
        """Ensure config is loaded, load if not."""
        if not self._loaded:
            self.load()

    def get_api(self, name: str) -> Optional[ApiDefinition]:
        """Get API definition by name."""
        self.ensure_loaded()
        return self.apis.get(name)

    def find_matching_api(self, text: str) -> Optional[Tuple[ApiDefinition, re.Match]]:
        """Find first API that matches the given text."""
        self.ensure_loaded()
        for api in self.apis.values():
            match = api.pattern.search(text)
            if match:
                return api, match
        return None

    def get_value_map(self, map_name: str) -> Dict[str, str]:
        """Get a value map by name."""
        self.ensure_loaded()
        return self.value_maps.get(map_name, {})

    def map_value(self, map_name: str, key: str, default: str = None) -> str:
        """Look up a value in a map."""
        self.ensure_loaded()
        value_map = self.value_maps.get(map_name, {})
        return value_map.get(key, default if default else key)

    def get_type_map(self, map_name: str) -> Dict[str, str]:
        """Get a type map by name."""
        self.ensure_loaded()
        return self.type_maps.get(map_name, {})

    def map_type(self, map_name: str, hlc_type: str) -> str:
        """Map an HLC type to N64 type."""
        self.ensure_loaded()
        type_map = self.type_maps.get(map_name, {})
        return type_map.get(hlc_type, hlc_type)

    def get_filter(self, filter_name: str) -> List[str]:
        """Get a filter list by name."""
        self.ensure_loaded()
        return self.filters.get(filter_name, [])

    def should_skip_type(self, type_name: str) -> bool:
        """Check if a type should be skipped based on prefix."""
        self.ensure_loaded()
        prefixes = self.filters.get('skip_type_prefixes', [])
        return any(type_name.startswith(p) for p in prefixes)

    def should_skip_member(self, member_name: str) -> bool:
        """Check if a member should be skipped."""
        self.ensure_loaded()
        skip_names = self.filters.get('skip_member_names', [])
        return member_name in skip_names

    def is_supported_type(self, type_name: str) -> bool:
        """Check if a type is supported for trait data."""
        self.ensure_loaded()
        supported = self.filters.get('supported_types', [])
        return type_name in supported


# Global config instance
_config: Optional[ApiConfig] = None


def get_config() -> ApiConfig:
    """Get the global API config instance, loading if necessary."""
    global _config
    if _config is None:
        _config = ApiConfig()
        _config.load()
    return _config


def reload_config():
    """Force reload of API config (useful for development)."""
    global _config
    _config = ApiConfig()
    _config.load()
    return _config


# =============================================================================
# Convenience functions for common lookups
# =============================================================================

def get_button_mapping(button_name: str) -> str:
    """Map Armory button name to N64 button enum."""
    return get_config().map_value('button_map', button_name.lower(), 'N64_BTN_A')


def get_input_state_func(method_name: str) -> str:
    """Map input method to N64 function."""
    return get_config().map_value('input_state_map', method_name.lower(), 'input_down')


def get_hlc_type_mapping(hlc_type: str) -> str:
    """Map HLC type to N64 C type."""
    return get_config().map_type('hlc_to_n64', hlc_type)


def get_skip_member_names() -> List[str]:
    """Get list of member names to skip."""
    return get_config().get_filter('skip_member_names')


def get_skip_type_prefixes() -> List[str]:
    """Get list of type prefixes to skip."""
    return get_config().get_filter('skip_type_prefixes')


def get_supported_types() -> List[str]:
    """Get list of supported primitive types."""
    return get_config().get_filter('supported_types')
