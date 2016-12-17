import bpy
import armutils
import os
import exporter
import assets
from material.shader_data import ShaderData
import material.make_forward as make_forward
import material.make_deferred as make_deferred
import material.mat_state as state

def parse(material, mat_data):
    state.material = material
    state.nodes = material.node_tree.nodes
    state.mat_data = mat_data

    state.path = armutils.get_fp() + '/build/compiled/ShaderRaws/' + material.name
    if not os.path.exists(state.path):
        os.makedirs(state.path)

    state.data = ShaderData(material)
    state.data.add_elem('pos', 3)
    state.data.add_elem('nor', 3)


    rid = exporter.ArmoryExporter.renderpath_id
    if rid == 'forward':
        make_context = make_forward
    elif rid == 'deferred':
       make_context = make_deferred

    rpasses = exporter.ArmoryExporter.renderpath_passes
    mesh_context_id = exporter.ArmoryExporter.mesh_context
    shadows_context_id = exporter.ArmoryExporter.shadows_context

    for rp in rpasses:
        
        if rp == mesh_context_id:
            c = make_mat_context(rp)
            const = {}
            const['name'] = 'receiveShadow'
            const['bool'] = material.receive_shadow
            c['bind_constants'].append(const)
            state.mat_context = c
            con = make_context.mesh(rp)

        elif rp == shadows_context_id:
            c = make_mat_context(rp)
            state.mat_context = c
            con = make_context.shadows(rp)

        else:
            continue
        
        write_shaders(con, rp)


    armutils.write_arm(state.path + '/' + material.name + '_data.arm', state.data.get())

    shader_data_name = material.name + '_data'
    shader_data_path = 'build/compiled/ShaderRaws/' + material.name + '/' + shader_data_name + '.arm'
    assets.add_shader_data(shader_data_path)
    mat_data['shader'] = shader_data_name + '/' + shader_data_name

    return state.data.sd

def make_mat_context(name):
    c = {}
    c['name'] = name
    state.mat_data['contexts'].append(c)
    c['bind_constants'] = []
    c['bind_textures'] = []
    return c

def write_shaders(con, rpass):
    if con.vert != None:
        shader_path = state.path + '/' + state.material.name + '_' + rpass + '.vert.glsl'
        assets.add_shader(shader_path)
        with open(shader_path, 'w') as f:
            f.write(con.vert.get())
    
    if con.frag != None:
        shader_path = state.path + '/' + state.material.name + '_' + rpass + '.frag.glsl'
        assets.add_shader(shader_path)
        with open(shader_path, 'w') as f:
            f.write(con.frag.get())
    
    if con.geom != None:
        shader_path = state.path + '/' + state.material.name + '_' + rpass + '.geom.glsl'
        assets.add_shader(shader_path)
        with open(shader_path, 'w') as f:
            f.write(con.geom.get())
    
    if con.tesc != None:
        shader_path = state.path + '/' + state.material.name + '_' + rpass + '.tesc.glsl'
        assets.add_shader(shader_path)
        with open(shader_path, 'w') as f:
            f.write(con.tesc.get())
    
    if con.tese != None:
        shader_path = state.path + '/' + state.material.name + '_' + rpass + '.tese.glsl'
        assets.add_shader(shader_path)
        with open(shader_path, 'w') as f:
            f.write(con.tese.get())
