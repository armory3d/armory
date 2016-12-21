import bpy
import armutils
import os
import assets
from material.shader_data import ShaderData
import material.cycles as cycles
import material.mat_state as mat_state
import material.mat_utils as mat_utils
import material.make_mesh as make_mesh
import material.make_shadowmap as make_shadowmap
import material.make_transluc as make_transluc
import material.make_overlay as make_overlay

def parse(material, mat_data, mat_users, rid):
    wrd = bpy.data.worlds['Arm']
    mat_state.material = material
    mat_state.nodes = material.node_tree.nodes
    mat_state.mat_data = mat_data
    mat_state.mat_users = mat_users
    mat_state.output_node = cycles.node_by_type(mat_state.nodes, 'OUTPUT_MATERIAL')
    if mat_state.output_node == None:
        return None
    matname = armutils.safe_source_name(material.name)
    mat_state.path = armutils.get_fp() + '/build/compiled/ShaderRaws/' + matname
    if not os.path.exists(mat_state.path):
        os.makedirs(mat_state.path)

    mat_state.data = ShaderData(material)
    mat_state.data.add_elem('pos', 3)
    mat_state.data.add_elem('nor', 3)

    if mat_users != None:
        for bo in mat_users[material]:
            # GPU Skinning
            if bo.find_armature() and armutils.is_bone_animation_enabled(bo) and wrd.generate_gpu_skin == True:
                mat_state.data.add_elem('bone', 4)
                mat_state.data.add_elem('weight', 4)
            
            # Instancing
            if bo.instanced_children or len(bo.particle_systems) > 0:
                mat_state.data.add_elem('off', 3)

    rpasses = mat_utils.get_rpasses(material)

    for rp in rpasses:
        c = {}
        c['name'] = rp
        c['bind_constants'] = []
        c['bind_textures'] = []
        mat_state.mat_data['contexts'].append(c)
        mat_state.mat_context = c

        if rp == 'mesh':
            const = {}
            const['name'] = 'receiveShadow'
            const['bool'] = material.receive_shadow
            c['bind_constants'].append(const)
            con = make_mesh.make(rp, rid)

        elif rp == 'shadowmap':
            con = make_shadowmap.make(rp, rpasses)

        elif rp == 'translucent':
            const = {}
            const['name'] = 'receiveShadow'
            const['bool'] = material.receive_shadow
            c['bind_constants'].append(const)
            con = make_transluc.make(rp)

        elif rp == 'overlay':
            con = make_overlay.make(rp)

        elif rp == 'decal':
            con = make_decal.make(rp)

        elif rp == 'depth':
            con = make_depth.make(rp)
        
        write_shaders(con, rp)

    armutils.write_arm(mat_state.path + '/' + matname + '_data.arm', mat_state.data.get())

    shader_data_name = matname + '_data'
    shader_data_path = 'build/compiled/ShaderRaws/' + matname + '/' + shader_data_name + '.arm'
    assets.add_shader_data(shader_data_path)
    mat_data['shader'] = shader_data_name + '/' + shader_data_name

    return mat_state.data.sd

def write_shaders(con, rpass):
    keep_cache = mat_state.material.is_cached
    write_shader(con.vert, 'vert', rpass, keep_cache)
    write_shader(con.frag, 'frag', rpass, keep_cache)
    write_shader(con.geom, 'geom', rpass, keep_cache)
    write_shader(con.tesc, 'tesc', rpass, keep_cache)
    write_shader(con.tese, 'tese', rpass, keep_cache)

def write_shader(shader, ext, rpass, keep_cache=True):
    if shader == None:
        return
    shader_path = mat_state.path + '/' + armutils.safe_source_name(mat_state.material.name) + '_' + rpass + '.' + ext + '.glsl'
    assets.add_shader(shader_path)
    if not os.path.isfile(shader_path) or not keep_cache:
        with open(shader_path, 'w') as f:
            f.write(shader.get())
