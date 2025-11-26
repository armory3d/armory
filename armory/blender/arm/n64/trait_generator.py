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
        f'void {func_name}_on_ready(void *entity);',
        f'void {func_name}_on_update(void *entity, float dt);',
        f'void {func_name}_on_remove(void *entity);',
    ]


def generate_trait_implementation(func_name: str, trait_class: str, trait_info: Dict = None) -> str:
    """
    Generate trait implementation from HLC scanner results.

    Args:
        func_name: C function name prefix (e.g., "rotator")
        trait_class: Original trait class name (e.g., "Rotator")
        trait_info: Data from HLC scanner with input_calls, transform_calls, etc.
    """
    lines = [f'// Trait: {trait_class}']

    # Generate on_ready
    lines.append(f'void {func_name}_on_ready(void *entity) {{')
    lines.append('    (void)entity;')
    lines.append('}')
    lines.append('')

    # Generate on_update with detected API calls
    lines.append(f'void {func_name}_on_update(void *entity, float dt) {{')
    lines.append('    (void)entity;')
    lines.append('    (void)dt;')

    if trait_info:
        # Generate input handling
        for call in trait_info.get('input_calls', []):
            button = call.get('button', 'a')
            method = call.get('method', 'down')
            n64_button = GAMEPAD_TO_N64_MAP.get(button.lower(), 'N64_BTN_A')
            n64_func = INPUT_STATE_MAP.get(method, 'input_down')
            lines.append(f'    if ({n64_func}({n64_button})) {{')
            lines.append(f'        // Handle {button} {method}')

            # Add transform code if this trait uses transforms
            for tcall in trait_info.get('transform_calls', []):
                tmethod = tcall.get('method', '')
                if tmethod == 'rotate':
                    lines.append('        // transform_rotate(entity, ...);')
                elif tmethod == 'translate':
                    lines.append('        // transform_translate(entity, ...);')

            # Add scene code if this trait uses scenes
            for scall in trait_info.get('scene_calls', []):
                smethod = scall.get('method', '')
                if smethod == 'setActive':
                    n64_func = SCENE_METHOD_MAP.get('setActive', 'scene_switch_to')
                    lines.append(f'        // {n64_func}("scene_name");')

            lines.append('    }')

    lines.append('}')
    lines.append('')

    # Generate on_remove
    lines.append(f'void {func_name}_on_remove(void *entity) {{')
    lines.append('    (void)entity;')
    lines.append('}')
    lines.append('')

    return '\n'.join(lines)


def generate_all_traits(trait_classes: Set[str], hlc_results: Dict = None) -> Tuple[str, str]:
    """
    Generate declarations and implementations for all traits.

    Args:
        trait_classes: Set of trait class names to generate
        hlc_results: Results from hlc_scanner.scan_and_summarize()

    Returns:
        Tuple of (declarations_str, implementations_str)
    """
    decl_lines = []
    impl_parts = []

    traits_data = hlc_results.get('traits', {}) if hlc_results else {}

    for trait_class in sorted(trait_classes):
        func_name = arm.utils.safesrc(trait_class).lower()
        decl_lines.extend(generate_trait_declaration(func_name))

        # Get trait-specific info from HLC scanner results
        trait_info = traits_data.get(trait_class)
        impl_parts.append(generate_trait_implementation(func_name, trait_class, trait_info))

    return '\n'.join(decl_lines), '\n'.join(impl_parts)


def write_traits_files(trait_classes: Set[str], hlc_results: Dict = None):
    """
    Write traits.h and traits.c files.

    Args:
        trait_classes: Set of trait class names to generate
        hlc_results: Results from hlc_scanner.scan_and_summarize()
    """
    declarations, implementations = generate_all_traits(trait_classes, hlc_results)

    # Write traits.h
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'traits.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'traits.h')
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()
    output = tmpl_content.format(trait_declarations=declarations)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Write traits.c
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'traits.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'traits.c')
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()
    output = tmpl_content.format(trait_implementations=implementations)
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
