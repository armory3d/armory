import bpy
import arm.nodes_renderpath as nodes_renderpath
import arm.utils

group = None
nodes = None
links = None

def make_renderer(cam):
    global group
    global nodes
    global links

    if cam.rp_renderer == 'Forward':
        load_library('forward_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_forward(cam)
    else: # Deferred
        load_library('deferred_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_deferred(cam)

def relink(start_node, next_node):
    if len(nodes[start_node].inputs[0].links) > 0:
        n = nodes[start_node].inputs[0].links[0].from_node
        l = n.outputs[0].links[0]
        links.remove(l)
        links.new(n.outputs[0], nodes[next_node].inputs[0])

def make_forward(cam):

    nodes['Begin'].inputs[1].default_value = cam.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(cam.rp_supersampling)

    if cam.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(cam.rp_shadowmap)
    else:
        l = nodes['Begin'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Begin'].outputs[0], nodes['Set Target Mesh'].inputs[0])
        relink('Bind Target Mesh SM', 'Draw Meshes Mesh') # No shadowmap bind
        relink('Bind Target Transluc SM', 'Draw Meshes Transluc')

    if not cam.rp_worldnodes:
        relink('Draw World', 'Set Target Accum')
        nodes['Clear Target Mesh'].inputs[1].default_value = True

    if not cam.rp_render_to_texture:
        links.new(nodes['Framebuffer'].outputs[0], nodes['Set Target Mesh'].inputs[1])
        if cam.rp_worldnodes:
            l = nodes['Draw World'].outputs[0].links[0]
        else:
            l = nodes['Draw Meshes Mesh'].outputs[0].links[0]
        links.remove(l)

    if not cam.rp_translucency:
        relink('Set Target Accum', 'Draw Compositor + FXAA')

    last_node = 'Draw Compositor + FXAA'
    if cam.rp_antialiasing == 'SMAA':
        pass
    elif cam.rp_antialiasing == 'TAA':
        pass
    elif cam.rp_antialiasing == 'FXAA':
        pass
    elif cam.rp_antialiasing == 'None':
        last_node = 'Draw Compositor'
        relink('Draw Compositor + FXAA', 'Draw Compositor')

    if cam.rp_overlays:
        links.new(last_node.outputs[0], nodes['Clear Target Overlay'].inputs[0])

def make_deferred(cam):

    nodes['Begin'].inputs[1].default_value = cam.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(cam.rp_supersampling)

    if cam.rp_voxelgi:
        links.new(nodes['Begin'].outputs[0], nodes['Clear Image Voxels'].inputs[0])
        links.new(nodes['Generate Mipmaps Voxels'].outputs[0], nodes['Set Target Mesh'].inputs[0])
        n = nodes['Image 3D Voxels']
        n.inputs[1].default_value = cam.rp_voxelgi_resolution[0]
        n.inputs[2].default_value = cam.rp_voxelgi_resolution[1]
        n.inputs[3].default_value = cam.rp_voxelgi_resolution[2]
        n = nodes['Set Viewport Voxels']
        n.inputs[1].default_value = cam.rp_voxelgi_resolution[0]
        n.inputs[2].default_value = cam.rp_voxelgi_resolution[1]
        links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Indirect'].inputs[4])

    if cam.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(cam.rp_shadowmap)
    else:
        l = nodes['Loop Lamps'].outputs[1].links[0]
        links.remove(l)
        links.new(nodes['Loop Lamps'].outputs[1], nodes['Deferred Light'].inputs[0])
        l = nodes['Deferred Light'].inputs[3].links[0] # No shadowmap bind
        links.remove(l)
        l = nodes['Volumetric Light'].inputs[6].links[0]
        links.remove(l)
        relink('Bind Target Transluc SM', 'Draw Meshes Transluc')

    # if not cam.rp_decals:
        # relink('Set Target.005', 'SSAO')

    if not cam.rp_ssao:
        relink('SSAO', 'Deferred Indirect')        
        l = nodes['Deferred Indirect'].inputs[3].links[0]
        links.remove(l)

    if not cam.rp_worldnodes:
        relink('Draw World', 'Set Target Accum')

    if not cam.rp_translucency:
        relink('Set Target Accum', 'Bloom')

    # if not cam.rp_bloom:
    relink('Bloom', 'SSR')

    if not cam.rp_ssr:
        relink('SSR', 'Draw Compositor')

    if bpy.data.worlds['Arm'].generate_ssr_half_res: # TODO: Move to cam
        links.new(nodes['ssra'].outputs[0], nodes['SSR'].inputs[2])
        links.new(nodes['ssrb'].outputs[0], nodes['SSR'].inputs[3])

    last_node = 'Draw Compositor'
    if not cam.rp_compositornodes:
        pass

    if cam.rp_overlays:
        links.new(nodes[last_node].outputs[0], nodes['Clear Target Overlay'].inputs[0])
        last_node = 'Draw Meshes Overlay'
        links.new(nodes[last_node].outputs[0], nodes['SMAA'].inputs[0])

    if cam.rp_antialiasing == 'SMAA':
        last_node = 'SMAA'
    elif cam.rp_antialiasing == 'TAA':
        last_node = 'Copy'
        links.new(nodes['SMAA'].outputs[0], nodes['TAA'].inputs[0])
        links.new(nodes['Reroute.019'].outputs[0], nodes['SMAA'].inputs[5])
        links.new(nodes['gbuffer2'].outputs[0], nodes['GBuffer'].inputs[2])
        links.new(nodes['Reroute.014'].outputs[0], nodes['SMAA'].inputs[1])
    elif cam.rp_antialiasing == 'FXAA':
        last_node = 'FXAA'
        relink('SMAA', 'FXAA')
    elif cam.rp_antialiasing == 'None':
        last_node = 'Draw Compositor'
        l = nodes['Draw Compositor'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Framebuffer'].outputs[0], nodes['Draw Compositor'].inputs[1])

# Handling node data
def check_default():
    if bpy.data.node_groups.get('armory_default') == None and len(bpy.data.cameras) > 0:
        make_renderer(bpy.data.cameras[0])

def reload_blend_data():
    if bpy.data.node_groups.get('Armory PBR') == None:
        load_library('Armory PBR')
    check_default()

def load_library(asset_name, rename=None):
    sdk_path = arm.utils.get_sdk_path()
    data_path = sdk_path + '/armory/blender/data/data.blend'
    data_names = [asset_name]

    # Remove old
    if rename != None and rename in bpy.data.node_groups and asset_name != 'Armory PBR':
        bpy.data.node_groups.remove(bpy.data.node_groups[rename], do_unlink=True)

    # Import
    data_refs = data_names.copy()
    with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
        data_to.node_groups = data_refs

    for ref in data_refs:
        ref.use_fake_user = True
        if rename != None:
            ref.name = rename

def register():
    reload_blend_data()

def unregister():
    pass
