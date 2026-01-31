"""
Koui Theme Parser - Parser for .ksn theme files with inheritance resolution.

This module handles parsing Koui theme files and resolving style inheritance
for N64 export.
"""

import os


class KouiThemeParser:
    """Parser for Koui .ksn theme files with inheritance resolution."""

    def __init__(self):
        self.globals = {}           # @globals variables
        self.selectors = {}         # Parsed selector styles: {selector_name: {properties}}
        self.resolved = {}          # Fully resolved styles (inheritance flattened)

    def parse_file(self, path: str):
        """Parse a .ksn theme file and merge into current state."""
        if not os.path.exists(path):
            return

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        current_section = None      # '@rules', '@globals', or selector name
        current_selector = None
        current_parent = None
        indent_stack = []           # Track indentation for nested properties
        property_path = []          # Current property path (e.g., ['color', 'text'])

        for line in content.split('\n'):
            # Skip comments and empty lines
            stripped = line.split('//')[0].rstrip()
            if not stripped:
                continue

            # Detect indentation level
            indent = len(line) - len(line.lstrip('\t'))

            # Section headers
            if stripped == '@rules:':
                current_section = 'rules'
                current_selector = None
                continue
            elif stripped == '@globals:':
                current_section = 'globals'
                current_selector = None
                continue
            elif stripped.endswith(':') and not stripped.startswith('\t'):
                # Selector line: "selector_name:" or "selector > parent:"
                current_section = 'selector'
                selector_part = stripped[:-1].strip()

                if ' > ' in selector_part:
                    current_selector, current_parent = selector_part.split(' > ')
                    current_selector = current_selector.strip()
                    current_parent = current_parent.strip()
                else:
                    current_selector = selector_part
                    current_parent = None

                if current_selector not in self.selectors:
                    self.selectors[current_selector] = {'_parent': current_parent}
                elif current_parent:
                    self.selectors[current_selector]['_parent'] = current_parent

                indent_stack = []
                property_path = []
                continue

            # Skip @rules section (schema definition)
            if current_section == 'rules':
                continue

            # Parse @globals
            if current_section == 'globals':
                if ': ' in stripped:
                    key, value = stripped.split(': ', 1)
                    self.globals[key.strip()] = value.strip()
                continue

            # Parse selector properties
            if current_section == 'selector' and current_selector:
                # Adjust property path based on indentation
                while indent_stack and indent <= indent_stack[-1]:
                    indent_stack.pop()
                    if property_path:
                        property_path.pop()

                if ': ' in stripped:
                    # Property assignment: "key: value"
                    key, value = stripped.split(': ', 1)
                    key = key.strip()
                    value = value.strip()

                    # Resolve variable references ($@globals.VAR or $_selector.path)
                    if value.startswith('$@globals.'):
                        var_name = value[10:]
                        value = self.globals.get(var_name, value)
                    elif value.startswith('$_'):
                        # Reference to another selector's property - skip for now
                        pass

                    # Build full property path
                    full_path = property_path + [key]
                    self._set_nested_property(self.selectors[current_selector], full_path, value)

                elif stripped.endswith(':'):
                    # Start of nested property group
                    key = stripped[:-1].strip()
                    if key.startswith('?'):
                        key = key[1:]  # Remove optional marker
                    indent_stack.append(indent)
                    property_path.append(key)

    def _set_nested_property(self, obj: dict, path: list, value):
        """Set a nested property in a dict using a path list."""
        for key in path[:-1]:
            if key not in obj:
                obj[key] = {}
            obj = obj[key]
        obj[path[-1]] = value

    def _get_nested_property(self, obj: dict, path: list, default=None):
        """Get a nested property from a dict using a path list."""
        for key in path:
            if not isinstance(obj, dict) or key not in obj:
                return default
            obj = obj[key]
        return obj

    def resolve_all(self):
        """Resolve all selectors with inheritance, flattening parent styles."""
        self.resolved = {}
        for selector in self.selectors:
            self.resolved[selector] = self._resolve_selector(selector)

    def _resolve_selector(self, selector: str, visited: set = None) -> dict:
        """Recursively resolve a selector's full style including parent inheritance."""
        if visited is None:
            visited = set()

        if selector in visited:
            return {}  # Circular reference protection
        visited.add(selector)

        if selector not in self.selectors:
            return {}

        raw = self.selectors[selector]
        parent_name = raw.get('_parent')

        # Start with parent's resolved style
        if parent_name:
            result = self._resolve_selector(parent_name, visited).copy()
            result = self._deep_merge(result, {})  # Deep copy
        else:
            result = {}

        # Merge current selector's properties (override parent)
        for key, value in raw.items():
            if key == '_parent':
                continue
            if isinstance(value, dict):
                if key not in result:
                    result[key] = {}
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dicts, with override taking precedence."""
        result = base.copy() if isinstance(base, dict) else {}
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get_style(self, selector: str) -> dict:
        """Get the fully resolved style for a selector."""
        return self.resolved.get(selector, {})

    def get_font_size(self, selector: str, default: int = 15) -> int:
        """Get font.size for a selector."""
        style = self.get_style(selector)
        try:
            return int(self._get_nested_property(style, ['font', 'size'], default))
        except (ValueError, TypeError):
            return default

    def get_text_color(self, selector: str, default: str = '#dddddd') -> str:
        """Get color.text for a selector as hex string."""
        style = self.get_style(selector)
        color = self._get_nested_property(style, ['color', 'text'], default)
        return color if color else default

    @staticmethod
    def parse_hex_color(hex_color: str) -> tuple:
        """Parse Koui hex color (#RRGGBB or #RRGGBBAA) to (r, g, b, a) tuple (0-255)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = 255
        elif len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
        else:
            return (221, 221, 221, 255)  # Default gray
        return (r, g, b, a)
