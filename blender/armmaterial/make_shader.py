import armutils
import os
import bpy
import assets
import armmaterial.mat_utils as mat_utils
import armmaterial.mat_state as mat_state
from armmaterial.shader_data import ShaderData
import armmaterial.cycles as cycles
import armmaterial.make_mesh as make_mesh
import armmaterial.make_shadowmap as make_shadowmap
import armmaterial.make_transluc as make_transluc
import armmaterial.make_overlay as make_overlay
import armmaterial.make_depth as make_depth
import armmaterial.make_decal as make_decal
import armmaterial.make_voxel as make_voxel

rpass_hook = None
mesh_make = make_mesh.make

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
        return None

    wrd = bpy.data.worlds['Arm']
    rpasses = mat_utils.get_rpasses(material)
    matname = armutils.safe_source_name(material.name)
    rel_path = 'build/compiled/ShaderRaws/' + matname
    full_path = armutils.get_fp() + '/' + rel_path
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    if mat_users != None:
        for bo in mat_users[material]:
            # GPU Skinning
            if bo.find_armature() and armutils.is_bone_animation_enabled(bo) and wrd.generate_gpu_skin == True:
                mat_state.data.add_elem('bone', 4)
                mat_state.data.add_elem('weight', 4)
            # Instancing
            if bo.instanced_children or len(bo.particle_systems) > 0:
                mat_state.data.add_elem('off', 3)

    bind_contants = dict()
    bind_textures = dict()

    for rp in rpasses:

        car = []
        bind_contants[rp] = car
        mat_state.bind_contants = car
        tar = []
        bind_textures[rp] = tar
        mat_state.bind_textures = tar

        if rp == 'mesh':
            con = mesh_make(rp, rid)

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

    armutils.write_arm(full_path + '/' + matname + '_data.arm', mat_state.data.get())
    shader_data_name = matname + '_data'
    shader_data_path = 'build/compiled/ShaderRaws/' + matname + '/' + shader_data_name + '.arm'
    assets.add_shader_data(shader_data_path)

    return rpasses, mat_state.data, shader_data_name, bind_contants, bind_textures

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
    shader_rel_path = rel_path + '/' + armutils.safe_source_name(mat_state.material.name) + '_' + rpass + '.' + ext + '.glsl'
    shader_path = armutils.get_fp() + '/' + shader_rel_path
    assets.add_shader(shader_rel_path)
    if not os.path.isfile(shader_path) or not keep_cache:
        with open(shader_path, 'w') as f:
            f.write(shader.get())
