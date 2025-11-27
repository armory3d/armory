"""
Config Loader - Configuration for N64 code generation.

Loads configuration files and provides lookup functions
for the code generator.

Configuration files (in config/ subdirectory):
  - api_mappings.json: Type maps and filters
  - input_mappings.json: Button and input state mappings
  - codegen_mappings.json: Code generation templates
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CodegenApiDef:
    """Code generation definition for an API call."""
    key: str                    # e.g., "transform.rotate"
    output: str                 # Output template, e.g., "it_rotate(&obj->transform, {x}, {y}, {z})"
    args: List[str]             # Arg names in order, e.g., ["x", "y", "z"]
    flags: Dict[str, bool]      # Context flags: needs_obj, needs_data, has_dt
    variants: Dict[str, str]    # Alternative output templates based on arg count or type


class ApiConfig:
    """Holds loaded and compiled API configuration."""

    def __init__(self):
        self.value_maps: Dict[str, Dict[str, str]] = {}
        self.type_maps: Dict[str, Dict[str, str]] = {}
        self.filters: Dict[str, List[str]] = {}
        self.codegen_apis: Dict[str, CodegenApiDef] = {}
        self._loaded = False

    def load(self, config_dir: str = None):
        """Load configuration from JSON files."""
        if config_dir is None:
            # Config files are in the config/ subdirectory
            config_dir = os.path.join(os.path.dirname(__file__), 'config')

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

        # Load codegen mappings
        codegen_path = os.path.join(config_dir, 'codegen_mappings.json')
        codegen_config = {}
        if os.path.exists(codegen_path):
            with open(codegen_path, 'r', encoding='utf-8') as f:
                codegen_config = json.load(f)

        self._parse_config(api_config, input_config, codegen_config)
        self._loaded = True

    def _parse_config(self, api_config: dict, input_config: dict, codegen_config: dict):
        """Parse loaded configs into compiled structures."""
        # Parse value maps - merge input mappings (excluding _comment keys)
        for key, value in input_config.items():
            if not key.startswith('_'):
                self.value_maps[key] = {k: v for k, v in value.items() if not k.startswith('_')}

        # Parse type maps
        self.type_maps = api_config.get('type_maps', {})

        # Parse filters
        self.filters = api_config.get('filters', {})

        # Parse codegen API definitions
        for key, api_def in codegen_config.get('apis', {}).items():
            self.codegen_apis[key] = CodegenApiDef(
                key=key,
                output=api_def.get('output', ''),
                args=api_def.get('args', {}),
                flags=api_def.get('flags', {}),
                variants=api_def.get('variants', {}),
            )

    def ensure_loaded(self):
        """Ensure config is loaded, load if not."""
        if not self._loaded:
            self.load()

    def get_codegen_api(self, target: str, method: str) -> Optional[CodegenApiDef]:
        """Get codegen API definition by target.method key."""
        self.ensure_loaded()
        key = f'{target.lower()}.{method.lower()}'
        return self.codegen_apis.get(key)

    def get_n64_button(self, button_name: str) -> str:
        """Map a button name to N64 button enum constant."""
        self.ensure_loaded()
        button_map = self.value_maps.get('button_map', {})
        return button_map.get(button_name.lower(), f'N64_BTN_{button_name.upper()}')


# Global config instance
_config: Optional[ApiConfig] = None


def get_config() -> ApiConfig:
    """Get the global API config instance, loading if necessary."""
    global _config
    if _config is None:
        _config = ApiConfig()
        _config.load()
    return _config
