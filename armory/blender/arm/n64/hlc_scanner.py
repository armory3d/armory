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
    member_values: Dict[str, float]  # {member_name: initial_value} for numeric members
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

            # For scene calls, capture the scene name variable
            if call_type == 'scene_setActive':
                scene_var = match.group(1) if len(match.groups()) >= 1 else None
                call_info['scene_var'] = scene_var

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


def find_member_string_assignments(code: str) -> Dict[str, str]:
    """
    Find string assignments to struct members.

    HLC generates patterns like:
        r3 = (String)s$Level_02;
        r0->nextLevel = r3;
    OR:
        this->nextLevel = (String)s$Level_02;

    Returns:
        {'nextLevel': 'Level_02', ...}
    """
    members = {}

    # First find all string constants
    string_consts = find_string_constants(code)

    # Pattern 1: varname->member = register;
    # where register was assigned a string constant
    member_assign = re.compile(r'\w+->(\w+)\s*=\s*(\w+)\s*;')

    for match in member_assign.finditer(code):
        member_name = match.group(1)
        value_var = match.group(2)
        if value_var in string_consts:
            members[member_name] = string_consts[value_var]

    # Pattern 2: Direct assignment: varname->member = (String)s$value;
    direct_pattern = re.compile(r'\w+->(\w+)\s*=\s*\(String\)s\$(\w+)\s*;')

    for match in direct_pattern.finditer(code):
        member_name = match.group(1)
        string_value = match.group(2)
        members[member_name] = string_value

    return members


def find_member_numeric_assignments(code: str) -> Dict[str, float]:
    """
    Find numeric assignments to struct members.

    HLC generates patterns like:
        r0->speed = 2.0;         (direct assignment)
    OR:
        r1 = 5.;                 (indirect assignment via local var)
        r0->speed = r1;

    Returns:
        {'speed': 2.0, ...}
    """
    members = {}

    # First, find all local variable numeric assignments: r1 = 5.;
    local_values = {}
    local_pattern = re.compile(r'(\w+)\s*=\s*(-?[\d.]+(?:e[+-]?\d+)?)\s*;', re.IGNORECASE)
    for match in local_pattern.finditer(code):
        var_name = match.group(1)
        try:
            value = float(match.group(2))
            local_values[var_name] = value
        except ValueError:
            pass

    # Pattern 1: Direct assignment - varname->member = number;
    direct_pattern = re.compile(r'\w+->(\w+)\s*=\s*(-?[\d.]+(?:e[+-]?\d+)?)\s*;', re.IGNORECASE)
    for match in direct_pattern.finditer(code):
        member_name = match.group(1)
        try:
            value = float(match.group(2))
            members[member_name] = value
        except ValueError:
            pass

    # Pattern 2: Indirect assignment via local var - varname->member = localvar;
    indirect_pattern = re.compile(r'\w+->(\w+)\s*=\s*(\w+)\s*;')
    for match in indirect_pattern.finditer(code):
        member_name = match.group(1)
        local_var = match.group(2)
        # Check if local_var was assigned a numeric value
        if local_var in local_values:
            members[member_name] = local_values[local_var]

    return members


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

    # Method 1: Find direct notifyOn calls with function pointer
    # Pattern: iron_Trait_notifyOnUpdate(something, arm_Rotator_new__$2);
    direct_notify = re.compile(r'iron_Trait_notifyOn(\w+)\s*\([^,]+,\s*(\w+)\s*\)')
    for match in direct_notify.finditer(content):
        lifecycle = match.group(1).lower()
        func_name = match.group(2)
        if func_name.startswith('arm_'):
            lifecycle_map[func_name] = lifecycle

    # Method 2: Find closure allocations that link function names to notify calls
    # Pattern: r3 = hl_alloc_closure_ptr(&t$..., arm_Rotator_new__$2, r0);
    # Then: iron_Trait_notifyOnUpdate(..., r3);
    notify_pattern = re.compile(
        r'(\w+)\s*=\s*hl_alloc_closure_ptr\s*\([^,]+,\s*(\w+)\s*,[^)]+\)\s*;'
        r'[^;]*iron_Trait_notifyOn(\w+)\s*\([^,]+,\s*\1\s*\)',
        re.DOTALL
    )

    for match in notify_pattern.finditer(content):
        func_name = match.group(2)
        lifecycle = match.group(3).lower()
        lifecycle_map[func_name] = lifecycle

    # Method 3: Also check for static closures
    static_notify_pattern = re.compile(
        r'static\s+vclosure\s+(\w+)\s*=\s*\{[^,]+,\s*(\w+)\s*,[^}]+\}\s*;'
        r'[^;]*iron_Trait_notifyOn(\w+)\s*\([^,]+,\s*&\1\s*\)',
        re.DOTALL
    )

    for match in static_notify_pattern.finditer(content):
        func_name = match.group(2)
        lifecycle = match.group(3).lower()
        lifecycle_map[func_name] = lifecycle

    # First pass: collect all member string assignments from all functions
    # This helps resolve member variables used in scene calls
    all_member_strings = {}
    all_member_numerics = {}
    func_pattern = re.compile(rf'void\s+(arm_{base_name}_new(?:__\$\d+)?)\s*\(')

    for match in func_pattern.finditer(content):
        func_name = match.group(1)
        body = extract_function_body(content, func_name)
        if body:
            member_strings = find_member_string_assignments(body)
            all_member_strings.update(member_strings)
            member_numerics = find_member_numeric_assignments(body)
            all_member_numerics.update(member_numerics)

    log.info(f"    Member string assignments: {all_member_strings}")
    log.info(f"    Member numeric assignments: {all_member_numerics}")

    # Second pass: parse functions with full context
    for match in func_pattern.finditer(content):
        func_name = match.group(1)
        body = extract_function_body(content, func_name)

        if body is None:
            continue

        # Get lifecycle from our map
        lifecycle = lifecycle_map.get(func_name)

        # Fallback: infer lifecycle from function name or content
        if lifecycle is None:
            if func_name == f'arm_{base_name}_new':
                lifecycle = 'constructor'
            elif 'iron_system_Time_get_delta' in body:
                # Functions using delta time are update functions
                lifecycle = 'update'
            elif any(pattern.search(body) for pattern in IRON_CALL_PATTERNS.values()):
                # Functions with Iron API calls (input, transform, scene) are likely update
                lifecycle = 'update'
            else:
                lifecycle = 'init'  # Default to init for functions without API calls

        # Find Iron API calls in this function
        calls = find_iron_calls(body)

        # Resolve string constants (local variables)
        string_consts = find_string_constants(body)
        for call in calls:
            # Resolve button names for input calls
            if 'button_var' in call and call['button_var'] in string_consts:
                call['button'] = string_consts[call['button_var']]
            # Resolve scene names for scene calls
            if 'scene_var' in call:
                scene_var = call['scene_var']
                # First try local string constants
                if scene_var in string_consts:
                    call['scene_name'] = string_consts[scene_var]
                else:
                    # Check if the scene variable is a member access (r0->member)
                    # Look for patterns like: r5 = r0->nextLevel;
                    member_access = re.search(rf'{scene_var}\s*=\s*\w+->(\w+)\s*;', body)
                    if member_access:
                        member_name = member_access.group(1)
                        if member_name in all_member_strings:
                            call['scene_name'] = all_member_strings[member_name]
                            log.info(f"      Resolved scene via member '{member_name}': {call['scene_name']}")

                    # Last resort: look for any Level_* or Scene_* string constant in the function
                    if 'scene_name' not in call:
                        scene_pattern = re.compile(r'\(String\)s\$(Level_\d+|Scene_\w+)', re.IGNORECASE)
                        scene_match = scene_pattern.search(body)
                        if scene_match:
                            call['scene_name'] = scene_match.group(1)
                            log.info(f"      Resolved scene from string constant: {call['scene_name']}")

        func_info = TraitFunction(
            name=func_name,
            lifecycle=lifecycle,
            body=body,
            calls=calls
        )
        functions.append(func_info)
        all_calls.extend(calls)

    return functions, all_calls, all_member_numerics


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

    # Parse source for functions, Iron calls, and member values
    functions, iron_calls, member_values = parse_trait_source(source_path)

    return TraitInfo(
        name=trait_name,
        c_name=c_name,
        header_file=header_path,
        source_file=source_path,
        struct_members=struct_members,
        member_values=member_values,
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
            if trait.member_values:
                log.info(f"    Member values: {trait.member_values}")
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
            'member_values': trait.member_values,  # Include numeric member values like speed
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
                    scene_name = call.get('scene_name', 'unknown')
                    trait_summary['scene_calls'].append({
                        'method': 'setActive',
                        'scene_name': scene_name,
                        'lifecycle': func.lifecycle,
                    })
                    summary['has_scene'] = True
                    summary.setdefault('scene_names', set()).add(scene_name)

                elif call['type'] == 'time_delta':
                    summary['has_time'] = True

        summary['traits'][name] = trait_summary

    # Convert sets to lists for JSON serialization
    summary['input_buttons'] = list(summary['input_buttons'])
    if 'scene_names' in summary:
        summary['scene_names'] = list(summary['scene_names'])

    return summary
