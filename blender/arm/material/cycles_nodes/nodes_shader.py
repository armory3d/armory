import bpy
from bpy.types import NodeSocket

import arm
import arm.material.cycles as c
from arm.material.parser_state import ParserState

if arm.is_reload(__name__):
    c = arm.reload_module(c)
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
    from arm.material.parser_state import ParserState
else:
    arm.enable_reload(__name__)


def parse_mixshader(node: bpy.types.ShaderNodeMixShader, out_socket: NodeSocket, state: ParserState) -> None:
    prefix = '' if node.inputs[0].is_linked else 'const '
    fac = c.parse_value_input(node.inputs[0])
    fac_var = c.node_name(node.name) + '_fac'
    fac_inv_var = c.node_name(node.name) + '_fac_inv'
    state.curshader.write('{0}float {1} = {2};'.format(prefix, fac_var, fac))
    state.curshader.write('{0}float {1} = 1.0 - {2};'.format(prefix, fac_inv_var, fac_var))
    bc1, rough1, met1, occ1, spec1, opac1, emi1 = c.parse_shader_input(node.inputs[1])
    bc2, rough2, met2, occ2, spec2, opac2, emi2 = c.parse_shader_input(node.inputs[2])
    if state.parse_surface:
        state.out_basecol = '({0} * {3} + {1} * {2})'.format(bc1, bc2, fac_var, fac_inv_var)
        state.out_roughness = '({0} * {3} + {1} * {2})'.format(rough1, rough2, fac_var, fac_inv_var)
        state.out_metallic = '({0} * {3} + {1} * {2})'.format(met1, met2, fac_var, fac_inv_var)
        state.out_occlusion = '({0} * {3} + {1} * {2})'.format(occ1, occ2, fac_var, fac_inv_var)
        state.out_specular = '({0} * {3} + {1} * {2})'.format(spec1, spec2, fac_var, fac_inv_var)
        state.out_emission = '({0} * {3} + {1} * {2})'.format(emi1, emi2, fac_var, fac_inv_var)
    if state.parse_opacity:
        state.out_opacity = '({0} * {3} + {1} * {2})'.format(opac1, opac2, fac_var, fac_inv_var)


def parse_addshader(node: bpy.types.ShaderNodeAddShader, out_socket: NodeSocket, state: ParserState) -> None:
    bc1, rough1, met1, occ1, spec1, opac1, emi1 = c.parse_shader_input(node.inputs[0])
    bc2, rough2, met2, occ2, spec2, opac2, emi2 = c.parse_shader_input(node.inputs[1])
    if state.parse_surface:
        state.out_basecol = '({0} + {1})'.format(bc1, bc2)
        state.out_roughness = '({0} * 0.5 + {1} * 0.5)'.format(rough1, rough2)
        state.out_metallic = '({0} * 0.5 + {1} * 0.5)'.format(met1, met2)
        state.out_occlusion = '({0} * 0.5 + {1} * 0.5)'.format(occ1, occ2)
        state.out_specular = '({0} * 0.5 + {1} * 0.5)'.format(spec1, spec2)
        state.out_emission = '({0} * 0.5 + {1} * 0.5)'.format(emi1, emi2)
    if state.parse_opacity:
        state.out_opacity = '({0} * 0.5 + {1} * 0.5)'.format(opac1, opac2)


def parse_bsdfprincipled(node: bpy.types.ShaderNodeBsdfPrincipled, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[20])
        state.out_basecol = c.parse_vector_input(node.inputs[0])
        # subsurface = c.parse_vector_input(node.inputs[1])
        # subsurface_radius = c.parse_vector_input(node.inputs[2])
        # subsurface_color = c.parse_vector_input(node.inputs[3])
        state.out_metallic = c.parse_value_input(node.inputs[6])
        state.out_specular = c.parse_value_input(node.inputs[7])
        # specular_tint = c.parse_vector_input(node.inputs[6])
        state.out_roughness = c.parse_value_input(node.inputs[9])
        # aniso = c.parse_vector_input(node.inputs[8])
        # aniso_rot = c.parse_vector_input(node.inputs[9])
        # sheen = c.parse_vector_input(node.inputs[10])
        # sheen_tint = c.parse_vector_input(node.inputs[11])
        # clearcoat = c.parse_vector_input(node.inputs[12])
        # clearcoat_rough = c.parse_vector_input(node.inputs[13])
        # ior = c.parse_vector_input(node.inputs[14])
        # transmission = c.parse_vector_input(node.inputs[15])
        # transmission_roughness = c.parse_vector_input(node.inputs[16])
        if node.inputs[20].is_linked or node.inputs[20].default_value != 0.0:
            state.out_emission = '({0}.x)'.format(c.parse_vector_input(node.inputs[20]))
            state.emission_found = True
        # clearcoar_normal = c.parse_vector_input(node.inputs[21])
        # tangent = c.parse_vector_input(node.inputs[22])
    if state.parse_opacity:
        if len(node.inputs) >= 21:
            state.out_opacity = c.parse_value_input(node.inputs[21])


def parse_bsdfdiffuse(node: bpy.types.ShaderNodeBsdfDiffuse, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[2])
        state.out_basecol = c.parse_vector_input(node.inputs[0])
        state.out_roughness = c.parse_value_input(node.inputs[1])
        state.out_specular = '0.0'


def parse_bsdfglossy(node: bpy.types.ShaderNodeBsdfGlossy, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[2])
        state.out_basecol = c.parse_vector_input(node.inputs[0])
        state.out_roughness = c.parse_value_input(node.inputs[1])
        state.out_metallic = '1.0'


def parse_ambientocclusion(node: bpy.types.ShaderNodeAmbientOcclusion, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        # Single channel
        state.out_occlusion = c.parse_vector_input(node.inputs[0]) + '.r'


def parse_bsdfanisotropic(node: bpy.types.ShaderNodeBsdfAnisotropic, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[4])
        # Revert to glossy
        state.out_basecol = c.parse_vector_input(node.inputs[0])
        state.out_roughness = c.parse_value_input(node.inputs[1])
        state.out_metallic = '1.0'


def parse_emission(node: bpy.types.ShaderNodeEmission, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        # Multiply basecol
        state.out_basecol = c.parse_vector_input(node.inputs[0])
        state.out_emission = '1.0'
        state.emission_found = True
        emission_strength = c.parse_value_input(node.inputs[1])
        state.out_basecol = '({0} * {1})'.format(state.out_basecol, emission_strength)


def parse_bsdfglass(node: bpy.types.ShaderNodeBsdfGlass, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[3])
        state.out_roughness = c.parse_value_input(node.inputs[1])
    if state.parse_opacity:
        state.out_opacity = '(1.0 - {0}.r)'.format(c.parse_vector_input(node.inputs[0]))


def parse_bsdfhair(node: bpy.types.ShaderNodeBsdfHair, out_socket: NodeSocket, state: ParserState) -> None:
    pass


def parse_holdout(node: bpy.types.ShaderNodeHoldout, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        # Occlude
        state.out_occlusion = '0.0'


def parse_bsdfrefraction(node: bpy.types.ShaderNodeBsdfRefraction, out_socket: NodeSocket, state: ParserState) -> None:
    # c.write_normal(node.inputs[3])
    pass


def parse_subsurfacescattering(node: bpy.types.ShaderNodeSubsurfaceScattering, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[4])
        state.out_basecol = c.parse_vector_input(node.inputs[0])


def parse_bsdftoon(node: bpy.types.ShaderNodeBsdfToon, out_socket: NodeSocket, state: ParserState) -> None:
    # c.write_normal(node.inputs[3])
    pass


def parse_bsdftranslucent(node: bpy.types.ShaderNodeBsdfTranslucent, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[1])
    if state.parse_opacity:
        state.out_opacity = '(1.0 - {0}.r)'.format(c.parse_vector_input(node.inputs[0]))


def parse_bsdftransparent(node: bpy.types.ShaderNodeBsdfTransparent, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_opacity:
        state.out_opacity = '(1.0 - {0}.r)'.format(c.parse_vector_input(node.inputs[0]))


def parse_bsdfvelvet(node: bpy.types.ShaderNodeBsdfVelvet, out_socket: NodeSocket, state: ParserState) -> None:
    if state.parse_surface:
        c.write_normal(node.inputs[2])
        state.out_basecol = c.parse_vector_input(node.inputs[0])
        state.out_roughness = '1.0'
        state.out_metallic = '1.0'
