"""
HashLink C Scanner

Scans HashLink C output (windows-hl-build) for trait definitions and
Iron API calls to generate N64-compatible C code.

This approach uses the Haxe→C compilation as source, which:
1. Preserves ALL Haxe logic (no pattern restrictions)
2. Already has C code structure (closer to N64 target)
3. Has trait struct definitions with state variables
4. Has clear function signatures for init/update/remove

The scanner parses the generated C files and translates
Iron/Kha API calls to N64/libdragon equivalents.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import arm
import arm.utils
import arm.log as log

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    log = arm.reload_module(log)
else:
    arm.enable_reload(__name__)


@dataclass
class TraitFunction:
    """Represents a trait lifecycle function (init, update, remove)."""
    name: str           # e.g., "arm_Rotator_new__$2"
    lifecycle: str      # "init", "update", "remove", "add"
    body: str           # The C function body
    calls: List[Dict]   # Iron API calls found in body


@dataclass
class TraitInfo:
    """Complete information about a parsed trait."""
    name: str           # e.g., "Rotator"
    c_name: str         # e.g., "arm__Rotator"
    header_file: str    # Path to .h file
    source_file: str    # Path to .c file
    struct_members: Dict[str, str]  # {member_name: type}
    functions: List[TraitFunction]
    iron_calls: List[Dict]  # All Iron API calls


# Iron API patterns to detect in HLC output
IRON_CALL_PATTERNS = {
    # Input
    'gamepad_down': re.compile(r'iron_system_Gamepad_down\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)'),
    'gamepad_started': re.compile(r'iron_system_Gamepad_started\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)'),
    'gamepad_released': re.compile(r'iron_system_Gamepad_released\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)'),

    # Transform
    'transform_rotate': re.compile(r'iron_object_Transform_rotate\s*\(\s*([^)]+)\)'),
    'transform_translate': re.compile(r'iron_object_Transform_translate\s*\(\s*([^)]+)\)'),
    'transform_move': re.compile(r'iron_object_Transform_move\s*\(\s*([^)]+)\)'),

    # Scene
    'scene_setActive': re.compile(r'iron_Scene_setActive\s*\(\s*(\w+)\s*,'),

    # Time
    'time_delta': re.compile(r'iron_system_Time_get_delta\s*\(\s*\)'),
}

# String constant pattern: (String)s$x -> "x"
STRING_CONST_PATTERN = re.compile(r'\(String\)s\$(\w+)')


def get_hlc_build_path() -> str:
    """Get the path to HashLink C build output."""
    build_dir = arm.utils.build_dir()

    possible_paths = [
        os.path.join(build_dir, 'windows-hl-build'),
        os.path.join(build_dir, 'linux-hl-build'),
        os.path.join(build_dir, 'osx-hl-build'),
    ]

    for path in possible_paths:
        if os.path.isdir(path):
            return path

    return possible_paths[0]


def find_trait_files(hlc_path: str) -> List[Tuple[str, str]]:
    """
    Find all trait C/H file pairs in the arm/ directory.

    Returns:
        List of (header_path, source_path) tuples
    """
    arm_dir = os.path.join(hlc_path, 'arm')
    if not os.path.isdir(arm_dir):
        log.warn(f"No arm/ directory found in {hlc_path}")
        return []

    traits = []
    for filename in os.listdir(arm_dir):
        if filename.endswith('.c'):
            base = filename[:-2]
            header = os.path.join(arm_dir, f'{base}.h')
            source = os.path.join(arm_dir, filename)
            if os.path.isfile(header):
                traits.append((header, source))

    return traits


def parse_struct_members(header_content: str, struct_name: str) -> Dict[str, str]:
    """
    Parse struct member definitions from header file.

    Example:
        struct _arm__Rotator {
            hl_type *$type;
            double speed;
            iron__system__Gamepad gamepad;
        };

    Returns:
        {'speed': 'double', 'gamepad': 'iron__system__Gamepad', ...}
    """
    members = {}

    # Find the struct definition
    pattern = rf'struct\s+{re.escape(struct_name)}\s*\{{([^}}]+)\}}'
    match = re.search(pattern, header_content, re.DOTALL)

    if not match:
        return members

    struct_body = match.group(1)

    # Parse each line for member declarations
    # Pattern: type member_name;
    member_pattern = re.compile(r'^\s*(\w[\w\s\*]+?)\s+(\w+)\s*;', re.MULTILINE)

    for m in member_pattern.finditer(struct_body):
        member_type = m.group(1).strip()
        member_name = m.group(2)

        # Skip HL runtime internals
        if member_name.startswith('$') or member_name.startswith('_'):
            continue
        if member_type in ('hl_type', 'vdynamic', 'varray'):
            continue

        members[member_name] = member_type

    return members


def extract_function_body(content: str, func_name: str) -> Optional[str]:
    """
    Extract the body of a C function.

    Returns the content between { and } for the function.
    """
    # Find function start
    pattern = rf'void\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{'
    match = re.search(pattern, content)

    if not match:
        return None

    start = match.end() - 1  # Include the opening brace
    depth = 1
    pos = start + 1

    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    return content[start:pos]


def find_iron_calls(code: str) -> List[Dict]:
    """
    Find all Iron API calls in a code block.

    Returns list of:
        {'type': 'gamepad_down', 'args': [...], 'line': code_snippet}
    """
    calls = []

    for call_type, pattern in IRON_CALL_PATTERNS.items():
        for match in pattern.finditer(code):
            call_info = {
                'type': call_type,
                'raw': match.group(0),
                'groups': match.groups(),
            }

            # Try to resolve string constants
            if call_type in ('gamepad_down', 'gamepad_started', 'gamepad_released'):
                # Second arg is the button string variable
                button_var = match.group(2) if len(match.groups()) >= 2 else None
                call_info['button_var'] = button_var

            calls.append(call_info)

    return calls


def find_string_constants(code: str) -> Dict[str, str]:
    """
    Find string constant assignments like: r4 = (String)s$x;

    Returns:
        {'r4': 'x', ...}
    """
    constants = {}

    # Pattern: varname = (String)s$value;
    pattern = re.compile(r'(\w+)\s*=\s*\(String\)s\$(\w+)\s*;')

    for match in pattern.finditer(code):
        var_name = match.group(1)
        string_value = match.group(2)
        constants[var_name] = string_value

    return constants


def parse_trait_source(source_path: str) -> Tuple[List[TraitFunction], List[Dict]]:
    """
    Parse a trait .c file to extract lifecycle functions and Iron API calls.

    Returns:
        (list of TraitFunction, list of all iron calls)
    """
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    functions = []
    all_calls = []

    # Get the trait base name from filename
    base_name = os.path.basename(source_path)[:-2]  # Remove .c

    # First, find what functions are registered for each lifecycle
    # Pattern: iron_Trait_notifyOnXxx(..., func_name, ...)
    lifecycle_map = {}  # func_name -> lifecycle

    # Find closure allocations that link function names to notify calls
    # Pattern: r3 = hl_alloc_closure_ptr(&t$..., arm_Rotator_new__$2, r0);
    # Then: iron_Trait_notifyOnUpdate(..., r3);

    # Simpler approach: find all notifyOn* calls and the function referenced before them
    notify_pattern = re.compile(
        r'(\w+)\s*=\s*hl_alloc_closure_ptr\s*\([^,]+,\s*(\w+)\s*,[^)]+\)\s*;'
        r'[^;]*iron_Trait_notifyOn(\w+)\s*\([^,]+,\s*\1\s*\)',
        re.DOTALL
    )

    for match in notify_pattern.finditer(content):
        func_name = match.group(2)
        lifecycle = match.group(3).lower()
        lifecycle_map[func_name] = lifecycle

    # Also check for static closures
    static_notify_pattern = re.compile(
        r'static\s+vclosure\s+(\w+)\s*=\s*\{[^,]+,\s*(\w+)\s*,[^}]+\}\s*;'
        r'[^;]*iron_Trait_notifyOn(\w+)\s*\([^,]+,\s*&\1\s*\)',
        re.DOTALL
    )

    for match in static_notify_pattern.finditer(content):
        func_name = match.group(2)
        lifecycle = match.group(3).lower()
        lifecycle_map[func_name] = lifecycle

    # Find all functions that belong to this trait
    func_pattern = re.compile(rf'void\s+(arm_{base_name}_new(?:__\$\d+)?)\s*\(')

    for match in func_pattern.finditer(content):
        func_name = match.group(1)
        body = extract_function_body(content, func_name)

        if body is None:
            continue

        # Get lifecycle from our map, or 'constructor' for the main new function
        lifecycle = lifecycle_map.get(func_name, 'constructor' if func_name == f'arm_{base_name}_new' else 'unknown')

        # Find Iron API calls in this function
        calls = find_iron_calls(body)

        # Resolve string constants
        string_consts = find_string_constants(body)
        for call in calls:
            if 'button_var' in call and call['button_var'] in string_consts:
                call['button'] = string_consts[call['button_var']]

        func_info = TraitFunction(
            name=func_name,
            lifecycle=lifecycle,
            body=body,
            calls=calls
        )
        functions.append(func_info)
        all_calls.extend(calls)

    return functions, all_calls


def parse_trait(header_path: str, source_path: str) -> TraitInfo:
    """
    Parse a complete trait from its header and source files.
    """
    trait_name = os.path.basename(header_path)[:-2]  # Remove .h
    c_name = f'_arm__{trait_name}'

    # Parse header for struct members
    with open(header_path, 'r', encoding='utf-8') as f:
        header_content = f.read()

    struct_members = parse_struct_members(header_content, c_name)

    # Parse source for functions and Iron calls
    functions, iron_calls = parse_trait_source(source_path)

    return TraitInfo(
        name=trait_name,
        c_name=c_name,
        header_file=header_path,
        source_file=source_path,
        struct_members=struct_members,
        functions=functions,
        iron_calls=iron_calls
    )


def scan_hlc_build(hlc_path: Optional[str] = None) -> Dict[str, TraitInfo]:
    """
    Scan the HashLink C build for all traits.

    Returns:
        Dictionary mapping trait name to TraitInfo
    """
    if hlc_path is None:
        hlc_path = get_hlc_build_path()

    if not os.path.isdir(hlc_path):
        log.warn(f"HLC build directory not found: {hlc_path}")
        return {}

    log.info(f"Scanning HLC build at: {hlc_path}")

    trait_files = find_trait_files(hlc_path)
    traits = {}

    for header_path, source_path in trait_files:
        try:
            trait = parse_trait(header_path, source_path)
            traits[trait.name] = trait

            log.info(f"  Trait '{trait.name}':")
            log.info(f"    Members: {list(trait.struct_members.keys())}")
            log.info(f"    Functions: {len(trait.functions)}")
            log.info(f"    Iron calls: {len(trait.iron_calls)}")

            for func in trait.functions:
                if func.calls:
                    call_types = [c['type'] for c in func.calls]
                    log.info(f"      {func.lifecycle}: {call_types}")

        except Exception as e:
            log.warn(f"Failed to parse trait {header_path}: {e}")

    return traits


def scan_and_summarize() -> Dict:
    """
    Convenience function to scan HLC build and return summary.

    Returns dict ready for N64 code generation.
    """
    traits = scan_hlc_build()

    summary = {
        'traits': {},
        'input_buttons': set(),
        'has_transform': False,
        'has_scene': False,
        'has_time': False,
    }

    for name, trait in traits.items():
        trait_summary = {
            'members': trait.struct_members,
            'functions': {},
            'input_calls': [],
            'transform_calls': [],
            'scene_calls': [],
        }

        for func in trait.functions:
            trait_summary['functions'][func.lifecycle] = {
                'name': func.name,
                'calls': func.calls,
            }

            for call in func.calls:
                if call['type'].startswith('gamepad_'):
                    button = call.get('button', 'unknown')
                    trait_summary['input_calls'].append({
                        'method': call['type'].replace('gamepad_', ''),
                        'button': button,
                        'lifecycle': func.lifecycle,
                    })
                    summary['input_buttons'].add(button)

                elif call['type'].startswith('transform_'):
                    trait_summary['transform_calls'].append({
                        'method': call['type'].replace('transform_', ''),
                        'lifecycle': func.lifecycle,
                    })
                    summary['has_transform'] = True

                elif call['type'] == 'scene_setActive':
                    trait_summary['scene_calls'].append({
                        'method': 'setActive',
                        'lifecycle': func.lifecycle,
                    })
                    summary['has_scene'] = True

                elif call['type'] == 'time_delta':
                    summary['has_time'] = True

        summary['traits'][name] = trait_summary

    # Convert set to list for JSON serialization
    summary['input_buttons'] = list(summary['input_buttons'])

    return summary
