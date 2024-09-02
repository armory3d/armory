"""
This module contains a list of all material nodes that Armory supports
(excluding output nodes), as well as Armory-related metadata.
"""
from enum import IntEnum, unique
from dataclasses import dataclass
from typing import Any, Callable, Optional

import bpy

import arm.material.arm_nodes.shader_data_node as shader_data_node
import arm.material.cycles_nodes.nodes_color as nodes_color
import arm.material.cycles_nodes.nodes_converter as nodes_converter
import arm.material.cycles_nodes.nodes_input as nodes_input
import arm.material.cycles_nodes.nodes_shader as nodes_shader
import arm.material.cycles_nodes.nodes_texture as nodes_texture
import arm.material.cycles_nodes.nodes_vector as nodes_vector
import arm.material.parser_state

if arm.is_reload(__name__):
    shader_data_node = arm.reload_module(shader_data_node)
    nodes_color = arm.reload_module(nodes_color)
    nodes_converter = arm.reload_module(nodes_converter)
    nodes_input = arm.reload_module(nodes_input)
    nodes_shader = arm.reload_module(nodes_shader)
    nodes_texture = arm.reload_module(nodes_texture)
    nodes_vector = arm.reload_module(nodes_vector)
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
else:
    arm.enable_reload(__name__)


@unique
class ComputeDXDYVariant(IntEnum):
    ALWAYS = 0
    """Always compute dx/dy variants of the corresponding node.
    Use this for input nodes that represent leafs of the node graph
    if some of their output values vary between fragments.
    """

    NEVER = 1
    """Never compute dx/dy variants of the corresponding node.
    Use this for nodes whose output values do not change with respect
    to fragment positions.
    """

    DYNAMIC = 2
    """Compute dx/dy variants if any input socket of the corresponding node
    is connected to a node that requires dx/dy variants.
    """


@dataclass
class MaterialNodeMeta:
    # Use Any here due to contravariance
    parse_func: Callable[[Any, bpy.types.NodeSocket, arm.material.parser_state.ParserState], Optional[str]]
    """The function used to parse this node and to translate it to GLSL output code."""

    compute_dxdy_variants: ComputeDXDYVariant = ComputeDXDYVariant.DYNAMIC
    """Specifies when this node should compute dx/dy variants
    if the ParserState is in the dx/dy offset pass.
    """


ALL_NODES: dict[str, MaterialNodeMeta] = {
    # --- nodes_color
    'BRIGHTCONTRAST': MaterialNodeMeta(parse_func=nodes_color.parse_brightcontrast),
    'CURVE_RGB': MaterialNodeMeta(parse_func=nodes_color.parse_curvergb),
    'GAMMA': MaterialNodeMeta(parse_func=nodes_color.parse_gamma),
    'HUE_SAT': MaterialNodeMeta(parse_func=nodes_color.parse_huesat),
    'INVERT': MaterialNodeMeta(parse_func=nodes_color.parse_invert),
    'LIGHT_FALLOFF': MaterialNodeMeta(parse_func=nodes_color.parse_lightfalloff),
    'MIX': MaterialNodeMeta(parse_func=nodes_color.parse_mix),

    # --- nodes_converter
    'BLACKBODY': MaterialNodeMeta(parse_func=nodes_converter.parse_blackbody),
    'CLAMP': MaterialNodeMeta(parse_func=nodes_converter.parse_clamp),
    'COMBHSV': MaterialNodeMeta(parse_func=nodes_converter.parse_combhsv),
    'COMBRGB': MaterialNodeMeta(parse_func=nodes_converter.parse_combrgb),
    'COMBXYZ': MaterialNodeMeta(parse_func=nodes_converter.parse_combxyz),
    'MAP_RANGE': MaterialNodeMeta(parse_func=nodes_converter.parse_maprange),
    'MATH': MaterialNodeMeta(parse_func=nodes_converter.parse_math),
    'RGBTOBW': MaterialNodeMeta(parse_func=nodes_converter.parse_rgbtobw),
    'SEPHSV': MaterialNodeMeta(parse_func=nodes_converter.parse_sephsv),
    'SEPRGB': MaterialNodeMeta(parse_func=nodes_converter.parse_seprgb),
    'SEPXYZ': MaterialNodeMeta(parse_func=nodes_converter.parse_sepxyz),
    'VALTORGB': MaterialNodeMeta(parse_func=nodes_converter.parse_valtorgb),  # ColorRamp
    'VECT_MATH': MaterialNodeMeta(parse_func=nodes_converter.parse_vectormath),
    'WAVELENGTH': MaterialNodeMeta(parse_func=nodes_converter.parse_wavelength),

    # --- nodes_input
    'ATTRIBUTE': MaterialNodeMeta(
        parse_func=nodes_input.parse_attribute,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'CAMERA': MaterialNodeMeta(
        parse_func=nodes_input.parse_camera,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'FRESNEL': MaterialNodeMeta(
        parse_func=nodes_input.parse_fresnel,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'HAIR_INFO': MaterialNodeMeta(parse_func=nodes_input.parse_hairinfo),
    'LAYER_WEIGHT': MaterialNodeMeta(
        parse_func=nodes_input.parse_layerweight,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'LIGHT_PATH': MaterialNodeMeta(
        parse_func=nodes_input.parse_lightpath,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),
    'NEW_GEOMETRY': MaterialNodeMeta(
        parse_func=nodes_input.parse_geometry,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'OBJECT_INFO': MaterialNodeMeta(
        parse_func=nodes_input.parse_objectinfo,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),
    'PARTICLE_INFO': MaterialNodeMeta(
        parse_func=nodes_input.parse_particleinfo,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),
    'RGB': MaterialNodeMeta(
        parse_func=nodes_input.parse_rgb,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),
    'TANGENT': MaterialNodeMeta(
        parse_func=nodes_input.parse_tangent,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'TEX_COORD': MaterialNodeMeta(
        parse_func=nodes_input.parse_texcoord,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'UVMAP': MaterialNodeMeta(
        parse_func=nodes_input.parse_uvmap,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    ),
    'VALUE': MaterialNodeMeta(
        parse_func=nodes_input.parse_value,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),
    'VERTEX_COLOR': MaterialNodeMeta(parse_func=nodes_input.parse_vertex_color),
    'WIREFRAME': MaterialNodeMeta(
        parse_func=nodes_input.parse_wireframe,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),

    # --- nodes_shader
    'ADD_SHADER': MaterialNodeMeta(parse_func=nodes_shader.parse_addshader),
    'AMBIENT_OCCLUSION': MaterialNodeMeta(parse_func=nodes_shader.parse_ambientocclusion),
    'BSDF_ANISOTROPIC': MaterialNodeMeta(parse_func=nodes_shader.parse_bsdfanisotropic),
    'BSDF_DIFFUSE': MaterialNodeMeta(parse_func=nodes_shader.parse_bsdfdiffuse),
    'BSDF_GLASS': MaterialNodeMeta(parse_func=nodes_shader.parse_bsdfglass),
    'BSDF_PRINCIPLED': MaterialNodeMeta(parse_func=nodes_shader.parse_bsdfprincipled),
    'BSDF_TRANSLUCENT': MaterialNodeMeta(parse_func=nodes_shader.parse_bsdftranslucent),
    'BSDF_TRANSPARENT': MaterialNodeMeta(parse_func=nodes_shader.parse_bsdftransparent),
    'BSDF_REFRACTION': MaterialNodeMeta(parse_func=nodes_shader.parse_bsdfrefraction),
    'EMISSION': MaterialNodeMeta(parse_func=nodes_shader.parse_emission),
    'HOLDOUT': MaterialNodeMeta(
        parse_func=nodes_shader.parse_holdout,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),
    'MIX_SHADER': MaterialNodeMeta(parse_func=nodes_shader.parse_mixshader),
    'SUBSURFACE_SCATTERING': MaterialNodeMeta(parse_func=nodes_shader.parse_subsurfacescattering),

    # --- nodes_texture
    'TEX_BRICK': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_brick),
    'TEX_CHECKER': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_checker),
    'TEX_ENVIRONMENT': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_environment),
    'TEX_GRADIENT': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_gradient),
    'TEX_IMAGE': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_image),
    'TEX_MAGIC': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_magic),
    'TEX_NOISE': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_noise),
    'TEX_POINTDENSITY': MaterialNodeMeta(
        parse_func=nodes_texture.parse_tex_pointdensity,
        compute_dxdy_variants=ComputeDXDYVariant.NEVER
    ),
    'TEX_SKY': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_sky),
    'TEX_VORONOI': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_voronoi),
    'TEX_WAVE': MaterialNodeMeta(parse_func=nodes_texture.parse_tex_wave),

    # --- nodes_vector
    'BUMP': MaterialNodeMeta(parse_func=nodes_vector.parse_bump),
    'CURVE_VEC': MaterialNodeMeta(parse_func=nodes_vector.parse_curvevec),
    'DISPLACEMENT': MaterialNodeMeta(parse_func=nodes_vector.parse_displacement),
    'MAPPING': MaterialNodeMeta(parse_func=nodes_vector.parse_mapping),
    'NORMAL': MaterialNodeMeta(parse_func=nodes_vector.parse_normal),
    'NORMAL_MAP': MaterialNodeMeta(parse_func=nodes_vector.parse_normalmap),
    'VECTOR_ROTATE': MaterialNodeMeta(parse_func=nodes_vector.parse_vectorrotate),
    'VECT_TRANSFORM': MaterialNodeMeta(parse_func=nodes_vector.parse_vectortransform),

    # --- arm_nodes
    'ArmShaderDataNode': MaterialNodeMeta(
        parse_func=shader_data_node.ShaderDataNode.parse,
        compute_dxdy_variants=ComputeDXDYVariant.ALWAYS
    )
}

if bpy.app.version > (3, 2, 0):
    ALL_NODES['SEPARATE_COLOR'] = MaterialNodeMeta(parse_func=nodes_converter.parse_separate_color)
    ALL_NODES['COMBINE_COLOR'] = MaterialNodeMeta(parse_func=nodes_converter.parse_combine_color)
if bpy.app.version < (4, 1, 0):
    ALL_NODES['BSDF_GLOSSY'] = MaterialNodeMeta(parse_func=nodes_shader.parse_bsdfglossy)
    ALL_NODES['BSDF_VELVET'] = MaterialNodeMeta(parse_func=nodes_shader.parse_bsdfvelvet)
    ALL_NODES['TEX_MUSGRAVE'] = MaterialNodeMeta(parse_func=nodes_texture.parse_tex_musgrave)

def get_node_meta(node: bpy.types.Node) -> MaterialNodeMeta:
    type_identifier = node.type if node.type != 'CUSTOM' else node.bl_idname
    return ALL_NODES[type_identifier]
