import os
import bpy
import arm.utils
import arm.assets as assets
import arm.material.mat_utils as mat_utils
import arm.material.mat_state as mat_state
from arm.material.shader_data import ShaderData
import arm.material.cycles as cycles
import arm.material.make_mesh as make_mesh
import arm.material.make_rect as make_rect
import arm.material.make_shadowmap as make_shadowmap
import arm.material.make_transluc as make_transluc
import arm.material.make_overlay as make_overlay
import arm.material.make_depth as make_depth
import arm.material.make_decal as make_decal
import arm.material.make_voxel as make_voxel

rpass_hook = None

def build(material, mat_users, mat_armusers, rid):
    mat_state.mat_users = mat_users
    mat_state.mat_armusers = mat_armusers
    mat_state.material = material
    mat_state.nodes = material.node_tree.nodes
    mat_state.data = ShaderData(material)
    mat_state.data.add_elem('pos', 3)
    mat_state.data.add_elem('nor', 3)
    mat_state.output_node = cycles.node_by_type(mat_state.nodes, 'OUTPUT_MATERIAL')
    if mat_state.output_node == None:
        # Place empty material output to keep compiler happy..
        mat_state.output_node = mat_state.nodes.new('ShaderNodeOutputMaterial')

    wrd = bpy.data.worlds['Arm']
    rpasses = mat_utils.get_rpasses(material)
    matname = arm.utils.safe_source_name(material.name)
    rel_path = 'build/compiled/ShaderRaws/' + matname
    full_path = arm.utils.get_fp() + '/' + rel_path
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    if mat_users != None:
        for bo in mat_users[material]:
            # GPU Skinning
            if arm.utils.export_bone_data(bo):
                mat_state.data.add_elem('bone', 4)
                mat_state.data.add_elem('weight', 4)
            # Instancing
            if bo.instanced_children or len(bo.particle_systems) > 0:
                mat_state.data.add_elem('off', 3)

    bind_constants = dict()
    bind_textures = dict()

    for rp in rpasses:

        car = []
        bind_constants[rp] = car
        mat_state.bind_constants = car
        tar = []
        bind_textures[rp] = tar
        mat_state.bind_textures = tar

        if rp == 'mesh':
            con = make_mesh.make(rp, rid)

        elif rp == 'rect':
            con = make_rect.make(rp)

        elif rp == 'shadowmap':
            con = make_shadowmap.make(rp, rpasses)

        elif rp == 'translucent':
            con = make_transluc.make(rp)

        elif rp == 'overlay':
            con = make_overlay.make(rp)

        elif rp == 'decal':
            con = make_decal.make(rp)

        elif rp == 'depth':
            con = make_depth.make(rp)

        elif rp == 'voxel':
            con = make_voxel.make(rp)

        elif rpass_hook != None:
            con = rpass_hook(rp)
        
        write_shaders(rel_path, con, rp)

    arm.utils.write_arm(full_path + '/' + matname + '_data.arm', mat_state.data.get())
    shader_data_name = matname + '_data'
    shader_data_path = 'build/compiled/ShaderRaws/' + matname + '/' + shader_data_name + '.arm'
    assets.add_shader_data(shader_data_path)

    return rpasses, mat_state.data, shader_data_name, bind_constants, bind_textures

def write_shaders(rel_path, con, rpass):
    keep_cache = mat_state.material.is_cached
    write_shader(rel_path, con.vert, 'vert', rpass, keep_cache)
    write_shader(rel_path, con.frag, 'frag', rpass, keep_cache)
    write_shader(rel_path, con.geom, 'geom', rpass, keep_cache)
    write_shader(rel_path, con.tesc, 'tesc', rpass, keep_cache)
    write_shader(rel_path, con.tese, 'tese', rpass, keep_cache)

def write_shader(rel_path, shader, ext, rpass, keep_cache=True):
    if shader == None:
        return
    shader_rel_path = rel_path + '/' + arm.utils.safe_source_name(mat_state.material.name) + '_' + rpass + '.' + ext + '.glsl'
    shader_path = arm.utils.get_fp() + '/' + shader_rel_path
    assets.add_shader(shader_rel_path)
    if not os.path.isfile(shader_path) or not keep_cache:
        with open(shader_path, 'w') as f:
            f.write(shader.get())
