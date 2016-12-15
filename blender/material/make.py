import armutils
import os
import exporter
from material.shader_data import ShaderData
import material.make_forward as make_forward
import material.make_deferred as make_deferred
import material.mat_state as state

def parse(self, material, mat_context, defs):
    state.material = material
    state.group = material.node_tree
    state.nodes = state.group.nodes
    state.links = state.group.links
    state.mat_context = mat_context
    state.defs = defs

    state.path = armutils.get_fp() + '/build/compiled/ShaderRaws/' + material.name
    if not os.path.exists(state.path):
        os.makedirs(state.path)

    state.data = ShaderData(material)
    state.data.add_elem('pos', 3)
    state.data.add_elem('nor', 3)

    rid = exporter.ArmoryExporter.renderpath_id
    if rid == 'forward':
        parse_forward()
    elif rid == 'deferred':
        parse_deferred()

    # TODO: Merge finalize shader here..
    armutils.write_arm(state.path + '/' + material.name + '_data.arm', state.data.get())

def parse_deferred():
    # Merge with fwd..
    rpasses = exporter.ArmoryExporter.renderpath_passes
    mesh_context_id = exporter.ArmoryExporter.mesh_context
    shadows_context_id = exporter.ArmoryExporter.shadows_context

    for rp in rpasses:
        if rp == mesh_context_id:
            con = make_deferred.mesh(rp)
        elif rp == shadows_context_id:
            con = make_deferred.shadows(rp)
        else:
            continue

        write_shaders(con, rp)

def parse_forward():
    rpasses = exporter.ArmoryExporter.renderpath_passes
    mesh_context_id = exporter.ArmoryExporter.mesh_context
    shadows_context_id = exporter.ArmoryExporter.shadows_context

    for rp in rpasses:
        if rp == mesh_context_id:
            con = make_forward.mesh(rp)
        elif rp == shadows_context_id:
            con = make_forward.shadows(rp)
        else:
            continue

        write_shaders(con, rp)

def write_shaders(con, rp):
    if con.vert != None:
        with open(state.path + '/' + state.material.name + '_' + rp + '.vert.glsl', 'w') as f:
            f.write(con.vert.get())
    if con.frag != None:
        with open(state.path + '/' + state.material.name + '_' + rp + '.frag.glsl', 'w') as f:
            f.write(con.frag.get())
    if con.geom != None:
        with open(state.path + '/' + state.material.name + '_' + rp + '.geom.glsl', 'w') as f:
            f.write(con.geom.get())
    if con.tesc != None:
        with open(state.path + '/' + state.material.name + '_' + rp + '.tesc.glsl', 'w') as f:
            f.write(con.tesc.get())
    if con.tese != None:
        with open(state.path + '/' + state.material.name + '_' + rp + '.tese.glsl', 'w') as f:
            f.write(con.tese.get())
