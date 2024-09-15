from typing import Generator

import bpy

import arm.utils
import arm.make_state as make_state
import arm.material.cycles as cycles
import arm.assets as assets
import arm.log as log

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    make_state = arm.reload_module(make_state)
    cycles = arm.reload_module(cycles)
    log = arm.reload_module(log)
else:
    arm.enable_reload(__name__)

add_mesh_contexts = []

def disp_linked(output_node):
    linked = output_node.inputs[2].is_linked
    if not linked:
        return False
    # Armory PBR with unlinked height socket
    l = output_node.inputs[2].links[0]
    if l.from_node.type == 'GROUP' and l.from_node.node_tree.name.startswith('Armory PBR') and \
        l.from_node.inputs[7].is_linked == False:
        return False
    disp_enabled = arm.utils.disp_enabled(make_state.target)
    rpdat = arm.utils.get_rp()
    if not disp_enabled and rpdat.arm_rp_displacement == 'Tessellation':
        log.warn('Tessellation not available on ' + make_state.target)
    return disp_enabled

def get_rpasses(material):
    ar = []

    rpdat = arm.utils.get_rp()
    has_voxels = arm.utils.voxel_support()

    if material.arm_decal:
        ar.append('decal')
    elif material.arm_overlay:
        ar.append('overlay')
    else:
        ar.append('mesh')
        for con in add_mesh_contexts:
            ar.append(con)
        if is_transluc(material) and not material.arm_discard and rpdat.rp_translucency_state != 'Off' and not material.arm_blending and not rpdat.rp_ss_refraction:
            ar.append('translucent')
        elif is_transluc(material) and not material.arm_discard and not material.arm_blending and rpdat.rp_ss_refraction:
            ar.append('refraction')
        if rpdat.rp_voxels != "Off" and has_voxels:
            ar.append('voxel')
        if rpdat.rp_renderer == 'Forward' and rpdat.rp_depthprepass and not material.arm_blending and not material.arm_particle_flag:
            ar.append('depth')

    if material.arm_cast_shadow and rpdat.rp_shadows and ('mesh' in ar):
        ar.append('shadowmap')

    return ar

def is_transluc(material):
    nodes = material.node_tree.nodes
    output_node = cycles.node_by_type(nodes, 'OUTPUT_MATERIAL')
    if output_node == None or output_node.inputs[0].is_linked == False:
        return False

    surface_node = output_node.inputs[0].links[0].from_node
    return is_transluc_traverse(surface_node)

def is_transluc_traverse(node):
    # TODO: traverse groups
    if is_transluc_type(node):
        return True
    for inp in node.inputs:
        if inp.is_linked:
            res = is_transluc_traverse(inp.links[0].from_node)
            if res:
                return True
    return False


def is_transluc_type(node: bpy.types.ShaderNode) -> bool:
    return node.type in ('BSDF_GLASS', 'BSDF_TRANSPARENT', 'BSDF_TRANSLUCENT', 'BSDF_REFRACTION') \
        or (is_armory_pbr_node(node) and (node.inputs['Opacity'].is_linked or node.inputs['Opacity'].default_value != 1.0)) \
        or (node.type == 'BSDF_PRINCIPLED' and (node.inputs['Alpha'].is_linked or node.inputs['Alpha'].default_value != 1.0))


def is_armory_pbr_node(node: bpy.types.ShaderNode) -> bool:
    return node.type == 'GROUP' and node.node_tree.name.startswith('Armory PBR')


def iter_nodes_armorypbr(node_group: bpy.types.NodeTree) -> Generator[bpy.types.Node, None, None]:
    for node in node_group.nodes:
        if is_armory_pbr_node(node):
            yield node


def equals_color_socket(socket: bpy.types.NodeSocketColor, value: tuple[float, ...], *, comp_alpha=True) -> bool:
    # NodeSocketColor.default_value is of bpy_prop_array type that doesn't
    # support direct comparison
    return (
        socket.default_value[0] == value[0]
        and socket.default_value[1] == value[1]
        and socket.default_value[2] == value[2]
        and (socket.default_value[3] == value[3] if comp_alpha else True)
    )
