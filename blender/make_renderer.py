import bpy
import nodes_renderpath

group = None
nodes = None
links = None

def make_renderer(cam):
    global group
    global nodes
    global links

    if cam.rp_renderer == 'Forward':
        nodes_renderpath.load_library('forward_path_high', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_forward(cam)
    else: # Deferred
        nodes_renderpath.load_library('deferred_path_high', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_deferred(cam)

def relink(start_node, next_node):
    n = nodes[start_node].inputs[0].links[0].from_node
    l = n.outputs[0].links[0]
    links.remove(l)
    links.new(n.outputs[0], nodes[next_node].inputs[0])

def make_forward(cam):

    if not cam.rp_hdr:
        nodes['Begin'].inputs[5].default_value = False

    if cam.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(cam.rp_shadowmap)

    if cam.rp_supersampling != '1':
        nodes['Screen'].inputs[0].default_value = int(cam.rp_supersampling)

    if not cam.rp_worldnodes:
        relink('Draw World', 'Clear Target.002')

    if not cam.rp_overlays:
        relink('Clear Target.002', 'Set Target.004')

    if not cam.rp_translucency:
        relink('Set Target.004', 'Draw Compositor + FXAA')

def make_deferred(cam):

    if not cam.rp_hdr:
        nodes['Begin'].inputs[5].default_value = False

    if cam.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(cam.rp_shadowmap)

    if cam.rp_supersampling != '1':
        nodes['Screen'].inputs[0].default_value = int(cam.rp_supersampling)

    if not cam.rp_worldnodes:
        relink('Draw World', 'Set Target.002')

    if not cam.rp_translucency:
        relink('Set Target.002', 'Bloom')

    if not cam.rp_overlays:
        relink('Clear Target.004', 'SMAA')

    if not cam.rp_decals:
        relink('Set Target.005', 'SSAO')

    if not cam.rp_ssao:
        relink('SSAO', 'Deferred Indirect')        
        l = nodes['Deferred Indirect'].inputs[3].links[0]
        links.remove(l)

    if not cam.rp_bloom:
        relink('Bloom', 'SSR')

    if not cam.rp_ssr:
        relink('SSR', 'Draw Compositor')

    if cam.rp_compositornodes:
        pass

    if cam.rp_antialiasing == 'SMAA':
        l = nodes['SMAA'].outputs[0].links[0]
        links.remove(l)
        n = nodes['Framebuffer']
        links.new(n.outputs[0], nodes['SMAA'].inputs[1])
        l = nodes['SMAA'].inputs[5].links[0] # Veloc
        links.remove(l)
        l = nodes['GBuffer'].inputs[2].links[0]
        links.remove(l)
    elif cam.rp_antialiasing == 'FXAA' or cam.rp_antialiasing == 'None':
        relink('SMAA', 'FXAA')
        l = nodes['GBuffer'].inputs[2].links[0]
        links.remove(l)
