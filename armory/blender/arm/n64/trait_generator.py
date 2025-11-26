"""
N64 Trait Generator

Generates N64 C code for traits based on HashLink C scanner results.
"""

import os
from typing import Dict, Set, List, Tuple

import arm
import arm.utils
import arm.log as log
from arm.n64.input_mapping import GAMEPAD_TO_N64_MAP, INPUT_STATE_MAP, SCENE_METHOD_MAP


if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    log = arm.reload_module(log)
else:
    arm.enable_reload(__name__)


def generate_trait_declaration(func_name: str) -> List[str]:
    """Generate function declarations for a trait."""
    return [
        f'void {func_name}_on_ready(void *entity, void *data);',
        f'void {func_name}_on_update(void *entity, float dt, void *data);',
        f'void {func_name}_on_remove(void *entity, void *data);',
    ]


# Map HLC C types to N64 C types (only these types are supported)
# Note: String is excluded - too complex for static C struct initialization
HLC_TYPE_MAP = {
    'double': 'float',      # N64 prefers float
    'float': 'float',
    'int': 'int32_t',
    'bool': 'bool',
}

# Types/prefixes to skip (Iron runtime internals, not user data)
SKIP_TYPE_PREFIXES = (
    'iron__',       # Iron runtime types
    'kha__',        # Kha framework types
    'armory__',     # Armory internal types
    'hl_',          # HashLink runtime types
    'vdynamic',     # HL dynamic types
    'varray',       # HL array types
)

SKIP_MEMBER_NAMES = (
    'object',       # Reference to parent object
    'transform',    # Reference to transform
    'gamepad',      # Input device reference
    'keyboard',     # Input device reference
    'mouse',        # Input device reference
    'name',         # Trait name - not needed at runtime
)


def generate_trait_data_struct(func_name: str, trait_class: str, trait_info: Dict = None) -> str:
    """
    Generate a data struct for traits that need per-instance data.

    Automatically includes ALL members extracted from HLC, not just hardcoded ones.
    Only includes primitive types that can be mapped to N64 C types.
    Returns empty string if no data struct is needed.
    """
    if not trait_info:
        return ''

    scene_calls = trait_info.get('scene_calls', [])
    members = trait_info.get('members', {})  # {name: hlc_type}

    # Determine what fields we need
    fields = []

    # If trait switches scenes, need target_scene field
    if scene_calls:
        fields.append('    SceneId target_scene;')

    # Add member variables from the trait (only supported primitive types)
    for member_name, hlc_type in members.items():
        # Skip internal/runtime members by name
        if member_name.startswith('_') or member_name.startswith('$'):
            continue
        if member_name in SKIP_MEMBER_NAMES:
            continue

        # Skip Iron/Kha/internal types - only include primitives we can map
        if any(hlc_type.startswith(prefix) for prefix in SKIP_TYPE_PREFIXES):
            continue

        # Only include types we have a mapping for (primitives)
        if hlc_type not in HLC_TYPE_MAP:
            continue

        c_type = HLC_TYPE_MAP[hlc_type]
        fields.append(f'    {c_type} {member_name};')

    if not fields:
        return ''

    struct_name = f'{trait_class}Data'
    return f'typedef struct {{\n' + '\n'.join(fields) + f'\n}} {struct_name};\n'


def generate_trait_implementation(func_name: str, trait_class: str, trait_info: Dict = None, valid_scene_names: List[str] = None) -> str:
    """
    Generate trait implementation from HLC scanner results.

    Args:
        func_name: C function name prefix (e.g., "rotator")
        trait_class: Original trait class name (e.g., "Rotator")
        trait_info: Data from HLC scanner with input_calls, transform_calls, etc.
        valid_scene_names: List of valid Blender scene names (for validation)
    """
    lines = [f'// Trait: {trait_class}']

    # Determine if this trait needs data
    needs_data = False
    if trait_info:
        scene_calls = trait_info.get('scene_calls', [])
        members = trait_info.get('members', {})
        needs_data = bool(scene_calls) or 'speed' in members

    # Generate on_ready
    lines.append(f'void {func_name}_on_ready(void *entity, void *data) {{')
    lines.append('    (void)entity;')
    lines.append('    (void)data;')
    lines.append('}')
    lines.append('')

    # Generate on_update with detected API calls
    lines.append(f'void {func_name}_on_update(void *entity, float dt, void *data) {{')

    has_time_delta = False
    has_transform = False
    has_scene = False
    uses_obj = False
    user_members = {}  # Supported user-defined members (primitives only)

    if trait_info:
        # Check if trait uses time delta (for continuous transforms)
        functions = trait_info.get('functions', {})
        for lifecycle, func_data in functions.items():
            for call in func_data.get('calls', []):
                if call.get('type') == 'time_delta':
                    has_time_delta = True
                    break

        transform_calls = trait_info.get('transform_calls', [])
        has_transform = len(transform_calls) > 0
        uses_obj = has_transform  # We use obj for transform calls

        scene_calls = trait_info.get('scene_calls', [])
        has_scene = len(scene_calls) > 0

        # Get supported user-defined trait members (primitives only)
        members = trait_info.get('members', {})
        for name, typ in members.items():
            # Skip internal members by name
            if name.startswith('_') or name.startswith('$'):
                continue
            if name in SKIP_MEMBER_NAMES:
                continue
            # Skip non-primitive types
            if any(typ.startswith(prefix) for prefix in SKIP_TYPE_PREFIXES):
                continue
            if typ not in HLC_TYPE_MAP:
                continue
            user_members[name] = typ

    # Determine if this trait needs data struct access
    needs_data_access = has_scene or bool(user_members)

    # Only declare obj if we use it
    if uses_obj:
        lines.append('    ArmObject *obj = (ArmObject *)entity;')
    else:
        lines.append('    (void)entity;')

    if trait_info:
        if not has_time_delta:
            lines.append('    (void)dt;')

        # Cast data pointer if needed (for ANY user members, not just speed)
        if needs_data_access:
            lines.append(f'    {trait_class}Data *tdata = ({trait_class}Data *)data;')
        else:
            lines.append('    (void)data;')

        # Separate input-triggered actions from continuous actions
        input_calls = trait_info.get('input_calls', [])

        # Find a numeric member that could be used as speed/rate
        # Priority: 'speed' > 'rate' > 'velocity' > first float member
        speed_member = None
        for name in ('speed', 'rate', 'velocity', 'rotationSpeed', 'moveSpeed'):
            if name in user_members:
                speed_member = name
                break
        if not speed_member:
            # Use first float/double member as fallback
            for name, typ in user_members.items():
                if typ in ('float', 'double'):
                    speed_member = name
                    break

        # Generate input handling blocks
        for call in input_calls:
            button = call.get('button', 'a')
            method = call.get('method', 'down')
            n64_button = GAMEPAD_TO_N64_MAP.get(button.lower(), 'N64_BTN_A')
            n64_func = INPUT_STATE_MAP.get(method, 'input_down')

            lines.append(f'    if ({n64_func}({n64_button})) {{')

            # For 'started' actions, scene switching is common
            if method == 'started' and has_scene:
                # Use trait data for scene target - this allows per-instance scene targets!
                lines.append(f'        scene_switch_to(tdata->target_scene);')

            # For 'down' (held) actions, transforms are common
            if method == 'down':
                for tcall in transform_calls:
                    tmethod = tcall.get('method', '')
                    # Use speed member from trait data if available
                    speed_val = f'tdata->{speed_member} * dt' if speed_member else 'dt'
                    if tmethod == 'rotate':
                        lines.append(f'        it_rotate(&obj->transform, 0.0f, {speed_val}, 0.0f);')
                    elif tmethod == 'translate':
                        lines.append(f'        it_translate(&obj->transform, 0.0f, 0.0f, {speed_val});')
                    elif tmethod == 'move':
                        lines.append(f'        it_translate(&obj->transform, 0.0f, 0.0f, {speed_val});')

            lines.append('    }')

        # If there are transforms without input (continuous rotation), add them outside input blocks
        if transform_calls and not input_calls:
            speed_val = f'tdata->{speed_member} * dt' if speed_member else 'dt'
            for tcall in transform_calls:
                tmethod = tcall.get('method', '')
                if tmethod == 'rotate':
                    lines.append(f'    // Continuous rotation')
                    lines.append(f'    it_rotate(&obj->transform, 0.0f, {speed_val}, 0.0f);')
    else:
        # No trait info - suppress all warnings
        lines.append('    (void)dt;')
        lines.append('    (void)data;')

    lines.append('}')
    lines.append('')

    # Generate on_remove
    lines.append(f'void {func_name}_on_remove(void *entity, void *data) {{')
    lines.append('    (void)entity;')
    lines.append('    (void)data;')
    lines.append('}')
    lines.append('')

    return '\n'.join(lines)


def generate_all_traits(trait_classes: Set[str], hlc_results: Dict = None) -> Tuple[str, str, str]:
    """
    Generate declarations, data structs, and implementations for all traits.

    Args:
        trait_classes: Set of trait class names to generate
        hlc_results: Results from hlc_scanner.scan_and_summarize()

    Returns:
        Tuple of (declarations_str, data_structs_str, implementations_str)
    """
    decl_lines = []
    data_struct_parts = []
    impl_parts = []

    traits_data = hlc_results.get('traits', {}) if hlc_results else {}
    valid_scene_names = hlc_results.get('valid_scene_names', []) if hlc_results else []

    for trait_class in sorted(trait_classes):
        func_name = arm.utils.safesrc(trait_class).lower()
        decl_lines.extend(generate_trait_declaration(func_name))

        # Get trait-specific info from HLC scanner results
        trait_info = traits_data.get(trait_class)

        # Generate data struct if needed
        data_struct = generate_trait_data_struct(func_name, trait_class, trait_info)
        if data_struct:
            data_struct_parts.append(data_struct)

        impl_parts.append(generate_trait_implementation(func_name, trait_class, trait_info, valid_scene_names))

    return '\n'.join(decl_lines), '\n'.join(data_struct_parts), '\n'.join(impl_parts)


def generate_trait_data_instances(trait_data_instances: List[Tuple[str, str, str]]) -> Tuple[str, str]:
    """
    Generate trait data instance definitions and extern declarations.

    Args:
        trait_data_instances: List of (var_name, type_name, init_str) tuples

    Returns:
        Tuple of (definitions_str, extern_declarations_str)
    """
    definitions = []
    externs = []

    for var_name, type_name, init_str in trait_data_instances:
        definitions.append(f'{type_name} {var_name} = {{ {init_str} }};')
        externs.append(f'extern {type_name} {var_name};')

    return '\n'.join(definitions), '\n'.join(externs)


def write_traits_files(trait_classes: Set[str], hlc_results: Dict = None, trait_data_instances: List = None):
    """
    Write traits.h and traits.c files.

    Args:
        trait_classes: Set of trait class names to generate
        hlc_results: Results from hlc_scanner.scan_and_summarize()
        trait_data_instances: List of (var_name, type_name, init_str) for centralized trait data
    """
    if trait_data_instances is None:
        trait_data_instances = []

    declarations, data_structs, implementations = generate_all_traits(trait_classes, hlc_results)

    # Generate trait data instances
    data_definitions, data_externs = generate_trait_data_instances(trait_data_instances)

    # Write traits.h
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'traits.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'traits.h')
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()
    output = tmpl_content.format(
        trait_data_structs=data_structs,
        trait_declarations=declarations,
        trait_data_externs=data_externs
    )
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Write traits.c
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'traits.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'traits.c')
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()
    output = tmpl_content.format(
        trait_implementations=implementations,
        trait_data_definitions=data_definitions
    )
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Log what was generated
    traits_data = hlc_results.get('traits', {}) if hlc_results else {}
    traits_with_code = [t for t in trait_classes if t in traits_data]

    if traits_with_code:
        log.info(f'Generated traits with HLC data: {", ".join(sorted(traits_with_code))}')
    if trait_classes:
        traits_scaffold = set(trait_classes) - set(traits_with_code)
        if traits_scaffold:
            log.info(f'Generated trait scaffolds: {", ".join(sorted(traits_scaffold))}')
    else:
        log.info('No traits to generate')

    if trait_data_instances:
        log.info(f'Generated {len(trait_data_instances)} trait data instances in traits.c')
