"""
N64 Code Generator Package.

This package provides IR→C code generation for the N64 exporter.
Split from the original codegen.py monolith for maintainability.

Public API:
    get_trait_info() - Load and return trait IR from JSON
    prepare_traits_template_data() - Prepare data for traits.h/c templates
    prepare_autoload_template_data() - Prepare data for autoload templates
    convert_scene_data() - Apply coordinate conversion to scene data
    generate_* functions - Scene code generation helpers
"""

# Re-export public API from submodules
from arm.n64.codegen.trait_generator import (
    get_trait_info,
    load_traits_json,
    prepare_traits_template_data,
    TraitCodeGenerator,
)

from arm.n64.codegen.autoload_generator import (
    load_autoloads_json,
    prepare_autoload_template_data,
)

from arm.n64.codegen.scene_generator import (
    convert_scene_data,
    generate_transform_block,
    generate_trait_block,
    generate_camera_block,
    generate_light_block,
    generate_object_block,
    generate_physics_block,
    generate_contact_subscriptions_block,
    generate_scene_traits_block,
)

from arm.n64.codegen.ir_emitter import IREmitter
from arm.n64.codegen.autoload_emitter import AutoloadIREmitter

__all__ = [
    # Trait functions
    'get_trait_info',
    'load_traits_json',
    'prepare_traits_template_data',
    'TraitCodeGenerator',
    # Autoload functions
    'load_autoloads_json',
    'prepare_autoload_template_data',
    # Scene functions
    'convert_scene_data',
    'generate_transform_block',
    'generate_trait_block',
    'generate_camera_block',
    'generate_light_block',
    'generate_object_block',
    'generate_physics_block',
    'generate_contact_subscriptions_block',
    'generate_scene_traits_block',
    # Classes
    'IREmitter',
    'AutoloadIREmitter',
]
