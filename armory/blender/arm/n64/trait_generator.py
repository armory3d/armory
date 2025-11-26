import os
from typing import Dict, Set, List, Tuple

import arm
import arm.utils
import arm.log as log


if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    log = arm.reload_module(log)
else:
    arm.enable_reload(__name__)


def generate_trait_declaration(func_name: str) -> List[str]:
    return [
        f'void {func_name}_on_ready(void *entity);',
        f'void {func_name}_on_update(void *entity, float dt);',
        f'void {func_name}_on_remove(void *entity);',
    ]


def generate_trait_implementation(func_name: str, trait_class: str) -> str:
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'trait.c.j2')
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    return tmpl_content.format(
        func_name=func_name,
        trait_class=trait_class
    )


def generate_all_traits(trait_classes: Set[str]) -> Tuple[str, str]:
    decl_lines = []
    impl_parts = []

    for trait_class in sorted(trait_classes):
        func_name = arm.utils.safesrc(trait_class).lower()
        decl_lines.extend(generate_trait_declaration(func_name))
        impl_parts.append(generate_trait_implementation(func_name, trait_class))

    return '\n'.join(decl_lines), '\n'.join(impl_parts)


def write_traits_files(trait_classes: Set[str], scanner_results: Dict = None):
    declarations, implementations = generate_all_traits(trait_classes)

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

    if trait_classes:
        log.info(f'Generated traits for: {", ".join(sorted(trait_classes))}')
    else:
        log.info('No traits to generate')

