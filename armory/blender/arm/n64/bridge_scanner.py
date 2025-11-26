"""
N64 Bridge Scanner

Scans compiled krom.js for N64Bridge.* marker calls and extracts them
into a structured dictionary for C code generation.

N64Bridge markers are inline stubs in Iron APIs that get compiled into
the JavaScript output. This scanner detects those patterns and builds
a trait_list dictionary mapping traits to their bridge calls.
"""

import os
import re
from typing import Optional

import arm
import arm.utils

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

# Patterns to match N64Bridge calls in compiled JavaScript
# Haxe compiles to patterns like:
#   iron_n64_N64Bridge.input.started("a")
#   iron_n64_N64Bridge.input.down("x")
#   iron_n64_N64Bridge.transform.translate(obj, 1.0, 0.0, 0.0)
#
# Pattern breakdown:
#   iron_n64_N64Bridge  - the compiled class name
#   \.(\w+)             - the sub-object (input, transform, scene, object)
#   \.(\w+)             - the method name (started, down, translate, etc.)
#   \(([^)]*)\)         - the arguments

N64_BRIDGE_PATTERN = re.compile(
    r'iron_n64_N64Bridge\.(\w+)\.(\w+)\s*\(\s*([^)]*)\s*\)',
    re.MULTILINE
)

# Alternative pattern for direct N64Bridge calls (in case of different compilation)
N64_BRIDGE_PATTERN_ALT = re.compile(
    r'N64Bridge\.(\w+)\.(\w+)\s*\(\s*([^)]*)\s*\)',
    re.MULTILINE
)

# Pattern to identify trait/class context in compiled JS
# Haxe compiles classes with prototype assignments
TRAIT_CONTEXT_PATTERN = re.compile(
    r'var\s+(\w+)\s*=\s*function|(\w+)\.prototype\.(\w+)\s*=\s*function',
    re.MULTILINE
)


def get_krom_js_path() -> str:
    """Get the path to compiled krom.js file. Tries multiple possible locations."""
    build_dir = arm.utils.build_dir()

    # Try different possible paths
    possible_paths = [
        os.path.join(build_dir, 'debug', 'krom', 'krom.js'),
        os.path.join(build_dir, 'krom', 'krom.js'),
    ]

    for path in possible_paths:
        if os.path.isfile(path):
            print(f"[N64 Bridge Scanner] Found krom.js at: {path}")
            return path

    # Return the first path as default (will show error later)
    return possible_paths[0]


def scan_krom_js(krom_js_path: Optional[str] = None) -> dict:
    """
    Scan krom.js for N64Bridge marker calls.

    Args:
        krom_js_path: Optional path to krom.js. If None, uses default build path.

    Returns:
        Dictionary with structure:
        {
            'bridge_calls': [
                {
                    'method': 'input_down',
                    'args': ['GAMEPAD_A'],
                    'line': 1234,
                    'context': 'PlayerTrait'  # Optional trait context
                },
                ...
            ],
            'inputs': set(),      # Unique input identifiers found
            'scenes': set(),      # Scene operations found
            'objects': set(),     # Object names referenced
            'transforms': [],     # Transform operations
            'raw_content': str    # Original JS content for debugging
        }
    """
    if krom_js_path is None:
        krom_js_path = get_krom_js_path()

    result = {
        'bridge_calls': [],
        # Track which methods are used per category
        'input_methods': set(),      # e.g., {'started', 'down', 'getStickX', 'getStickY'}
        'transform_methods': set(),  # e.g., {'translate', 'rotate', 'setPosition'}
        'scene_methods': set(),      # e.g., {'setActive', 'getName'}
        'object_methods': set(),     # e.g., {'getVisible', 'setVisible'}
        # Legacy sets for backward compatibility
        'inputs': set(),
        'scenes': set(),
        'objects': set(),
        'transforms': [],
        'raw_content': '',
        'error': None
    }

    # Check if file exists
    if not os.path.isfile(krom_js_path):
        result['error'] = f"krom.js not found at: {krom_js_path}"
        print(f"[N64 Bridge Scanner] {result['error']}")
        return result

    # Read the file
    try:
        with open(krom_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        result['raw_content'] = content
    except Exception as e:
        result['error'] = f"Failed to read krom.js: {e}"
        print(f"[N64 Bridge Scanner] {result['error']}")
        return result

    # Find all N64Bridge calls using primary pattern
    for match in N64_BRIDGE_PATTERN.finditer(content):
        subobj = match.group(1)   # input, transform, scene, object
        method = match.group(2)   # started, down, translate, etc.
        args_str = match.group(3).strip()

        # Parse arguments (handle quoted strings and numbers)
        args = parse_args(args_str)

        # Get line number for debugging
        line_num = content[:match.start()].count('\n') + 1

        call_info = {
            'category': subobj,
            'method': method,
            'args': args,
            'line': line_num,
            'raw': match.group(0)
        }

        result['bridge_calls'].append(call_info)

        # Categorize by type
        categorize_call(call_info, result)

    # Try alternative pattern if nothing found
    if len(result['bridge_calls']) == 0:
        for match in N64_BRIDGE_PATTERN_ALT.finditer(content):
            subobj = match.group(1)
            method = match.group(2)
            args_str = match.group(3).strip()

            args = parse_args(args_str)
            line_num = content[:match.start()].count('\n') + 1

            call_info = {
                'category': subobj,
                'method': method,
                'args': args,
                'line': line_num,
                'raw': match.group(0)
            }

            result['bridge_calls'].append(call_info)
            categorize_call(call_info, result)

    # Print summary
    print(f"[N64 Bridge Scanner] Found {len(result['bridge_calls'])} N64Bridge calls")
    print(f"[N64 Bridge Scanner] Input methods: {result['input_methods']}")
    print(f"[N64 Bridge Scanner] Transform methods: {result['transform_methods']}")
    print(f"[N64 Bridge Scanner] Scene methods: {result['scene_methods']}")
    print(f"[N64 Bridge Scanner] Object methods: {result['object_methods']}")

    return result


def parse_args(args_str: str) -> list:
    """
    Parse argument string from JavaScript function call.

    Handles:
    - Quoted strings: "GAMEPAD_A" or 'GAMEPAD_A'
    - Numbers: 1.0, -5, 0
    - Variable references: obj, this.x
    """
    if not args_str:
        return []

    args = []
    current = ''
    in_string = False
    string_char = None
    depth = 0

    for char in args_str:
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
            current += char
        elif char == string_char and in_string:
            in_string = False
            string_char = None
            current += char
        elif char == '(' and not in_string:
            depth += 1
            current += char
        elif char == ')' and not in_string:
            depth -= 1
            current += char
        elif char == ',' and not in_string and depth == 0:
            args.append(clean_arg(current.strip()))
            current = ''
        else:
            current += char

    if current.strip():
        args.append(clean_arg(current.strip()))

    return args


def clean_arg(arg: str) -> str:
    """Clean and normalize an argument value."""
    # Remove surrounding quotes
    if (arg.startswith('"') and arg.endswith('"')) or \
       (arg.startswith("'") and arg.endswith("'")):
        return arg[1:-1]
    return arg


def categorize_call(call_info: dict, result: dict):
    """Categorize a bridge call by its type and update result sets."""
    category = call_info.get('category', '')
    method = call_info['method']
    args = call_info['args']

    # Input methods: input.started, input.down, input.released, input.getStickX, etc.
    if category == 'input':
        result['input_methods'].add(method)
        # Also track args for backward compatibility (though these are variable names)
        if args:
            result['inputs'].add(args[0])

    # Scene methods: scene.setActive, scene.getName
    elif category == 'scene':
        result['scene_methods'].add(method)
        result['scenes'].add(method)

    # Object methods: object.getVisible, object.setVisible
    elif category == 'object':
        result['object_methods'].add(method)

    # Transform methods: transform.translate, transform.rotate, etc.
    elif category == 'transform':
        result['transform_methods'].add(method)
        result['transforms'].append(call_info)


def build_trait_list(scan_result: dict) -> dict:
    """
    Build the trait_list dictionary from scan results.

    This is the main output structure used by N64Exporter for C code generation.

    Returns:
        {
            'input_methods': ['started', 'down', 'getStickX'],  # Which input methods are used
            'transform_methods': ['translate', 'rotate'],       # Which transform methods are used
            'scene_methods': ['setActive'],                     # Which scene methods are used
            'object_methods': ['getVisible', 'setVisible'],     # Which object methods are used
            'transforms': [                                     # Detailed transform calls
                {'type': 'translate', 'args': [...]},
            ],
        }
    """
    trait_list = {
        'input_methods': list(scan_result.get('input_methods', set())),
        'transform_methods': list(scan_result.get('transform_methods', set())),
        'scene_methods': list(scan_result.get('scene_methods', set())),
        'object_methods': list(scan_result.get('object_methods', set())),
        'transforms': [],
    }

    # Collect detailed transform operations
    for call in scan_result.get('bridge_calls', []):
        category = call.get('category', '')
        method = call['method']
        args = call['args']

        if category == 'transform':
            trait_list['transforms'].append({
                'type': method,
                'args': args
            })

    return trait_list


def scan_and_build() -> dict:
    """
    Convenience function to scan krom.js and build trait_list in one call.

    Returns:
        trait_list dictionary ready for C code generation.
    """
    scan_result = scan_krom_js()

    if scan_result.get('error'):
        print(f"[N64 Bridge Scanner] Error during scan: {scan_result['error']}")
        return {
            'input_methods': [],
            'transform_methods': [],
            'scene_methods': [],
            'object_methods': [],
            'transforms': [],
            'error': scan_result['error']
        }

    return build_trait_list(scan_result)
