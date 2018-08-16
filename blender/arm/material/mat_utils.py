import bpy
import arm.utils
import arm.make_state as make_state
import arm.material.cycles as cycles
import arm.log as log

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
    vgirefract = rpdat.rp_gi == 'Voxel GI' and rpdat.arm_voxelgi_refraction and has_voxels

    if material.arm_decal:
        ar.append('decal')
    elif material.arm_overlay:
        ar.append('overlay')
    elif is_transluc(material) and not material.arm_discard and not vgirefract and rpdat.rp_translucency_state != 'Off' and not material.arm_blending:
        ar.append('translucent')
    else:
        ar.append('mesh')
        for con in add_mesh_contexts:
            ar.append(con)
        if (rpdat.rp_gi == 'Voxel GI' or rpdat.rp_gi == 'Voxel AO') and has_voxels:
            ar.append('voxel')
        if rpdat.rp_renderer == 'Deferred Plus':
            ar.append('rect')
        if rpdat.rp_renderer == 'Forward' and rpdat.rp_depthprepass and not material.arm_blending and not material.arm_particle_flag:
            ar.append('depth')
            
    shadows_enabled = False
    if rpdat.rp_shadowmap != 'Off':
        shadows_enabled = True

    if material.arm_cast_shadow and shadows_enabled and ('mesh' in ar or 'translucent' in ar):
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

def is_transluc_type(node):
    if node.type == 'BSDF_GLASS' or \
       node.type == 'BSDF_TRANSPARENT' or \
       node.type == 'BSDF_TRANSLUCENT' or \
       (node.type == 'GROUP' and node.node_tree.name.startswith('Armory PBR') and (node.inputs[1].is_linked or node.inputs[1].default_value != 1.0)):
       return True
    return False
