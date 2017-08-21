import bpy
import arm.nodes_renderpath as nodes_renderpath
import arm.utils
import arm.assets as assets

group = None
nodes = None
links = None

updating_preset = False

def set_preset(self, context, preset):
    global updating_preset

    wrd = bpy.data.worlds['Arm']

    updating_preset = True

    if preset == 'Low':
        wrd.rp_renderer = 'Forward'
        wrd.arm_material_model = 'PBR'
        wrd.rp_shadowmap = '1024'
        wrd.rp_translucency_state = 'Off'
        wrd.rp_overlays_state = 'Off'
        wrd.rp_decals_state = 'Off'
        wrd.rp_sss_state = 'Off'
        wrd.rp_hdr = False
        wrd.rp_world = False
        wrd.rp_clearbackground = True
        wrd.rp_stereo = False
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = False
        wrd.rp_render_to_texture = False
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'None'
        wrd.rp_compositornodes = False
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = False
        wrd.rp_ssr = False
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'
    elif preset == 'Forward':
        wrd.rp_renderer = 'Forward'
        wrd.arm_material_model = 'PBR'
        wrd.rp_shadowmap = '2048'
        wrd.rp_translucency_state = 'Auto'
        wrd.rp_overlays_state = 'Auto'
        wrd.rp_decals_state = 'Auto'
        wrd.rp_sss_state = 'Auto'
        wrd.rp_hdr = True
        wrd.rp_world = True
        wrd.rp_clearbackground = False
        wrd.rp_stereo = False
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = False
        wrd.rp_render_to_texture = True
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'SMAA'
        wrd.rp_compositornodes = True
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = True
        wrd.rp_ssr = True
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'
    elif preset == 'Deferred':
        wrd.rp_renderer = 'Deferred'
        wrd.arm_material_model = 'PBR'
        wrd.rp_shadowmap = '2048'
        wrd.rp_translucency_state = 'Auto'
        wrd.rp_overlays_state = 'Auto'
        wrd.rp_decals_state = 'Auto'
        wrd.rp_sss_state = 'Auto'
        wrd.rp_hdr = True
        wrd.rp_world = True
        wrd.rp_clearbackground = False
        wrd.rp_stereo = False
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = False
        wrd.rp_render_to_texture = True
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'FXAA'
        wrd.rp_compositornodes = True
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = True
        wrd.rp_ssr = False
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'
    elif preset == 'Max':
        wrd.rp_renderer = 'Deferred'
        wrd.arm_material_model = 'PBR'
        wrd.rp_shadowmap = '4096'
        wrd.rp_translucency_state = 'Auto'
        wrd.rp_overlays_state = 'Auto'
        wrd.rp_decals_state = 'Auto'
        wrd.rp_sss_state = 'Auto'
        wrd.rp_hdr = True
        wrd.rp_world = True
        wrd.rp_clearbackground = False
        wrd.rp_stereo = False
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = False
        wrd.rp_render_to_texture = True
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'TAA'
        wrd.rp_compositornodes = True
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = True
        wrd.rp_ssr = True
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'
    elif preset == 'Render Capture':
        wrd.rp_renderer = 'Deferred'
        wrd.rp_shadowmap = '8192'
        wrd.rp_translucency_state = 'Auto'
        wrd.rp_overlays_state = 'Auto'
        wrd.rp_decals_state = 'Auto'
        wrd.rp_sss_state = 'Auto'
        wrd.rp_hdr = True
        wrd.rp_world = True
        wrd.rp_clearbackground = False
        wrd.rp_stereo = False
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = True
        wrd.rp_voxelgi_resolution = '256'
        wrd.rp_render_to_texture = True
        wrd.rp_supersampling = '2'
        wrd.rp_antialiasing = 'TAA'
        wrd.rp_compositornodes = True
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = True
        wrd.rp_ssr = True
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = True
        wrd.rp_rendercapture_format = '8bit'
        wrd.rp_motionblur = 'None'
        wrd.arm_material_model = 'Cycles'
        wrd.arm_pcss_state = 'On'
    elif preset == 'Deferred Plus':
        wrd.rp_renderer = 'Deferred Plus'
        wrd.arm_material_model = 'PBR'
        wrd.rp_shadowmap = '4096'
        wrd.rp_translucency_state = 'Auto'
        wrd.rp_overlays_state = 'Auto'
        wrd.rp_decals_state = 'Auto'
        wrd.rp_sss_state = 'Auto'
        wrd.rp_hdr = True
        wrd.rp_world = True
        wrd.rp_clearbackground = False
        wrd.rp_stereo = False
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = False
        wrd.rp_render_to_texture = True
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'TAA'
        wrd.rp_compositornodes = True
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = True
        wrd.rp_ssr = True
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'
    elif preset == 'VR Low':
        wrd.rp_renderer = 'Forward'
        wrd.arm_material_model = 'Restricted'
        wrd.rp_shadowmap = '1024'
        wrd.rp_translucency_state = 'Off'
        wrd.rp_overlays_state = 'Off'
        wrd.rp_decals_state = 'Off'
        wrd.rp_sss_state = 'Off'
        wrd.rp_hdr = False
        wrd.rp_world = False
        wrd.rp_clearbackground = True
        wrd.rp_stereo = True
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = False
        wrd.rp_render_to_texture = False
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'None'
        wrd.rp_compositornodes = False
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = False
        wrd.rp_ssr = False
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'
    elif preset == 'Mobile Low':
        wrd.rp_renderer = 'Forward'
        wrd.arm_material_model = 'Restricted'
        wrd.rp_shadowmap = '1024'
        wrd.rp_translucency_state = 'Off'
        wrd.rp_overlays_state = 'Off'
        wrd.rp_decals_state = 'Off'
        wrd.rp_sss_state = 'Off'
        wrd.rp_hdr = False
        wrd.rp_world = False
        wrd.rp_clearbackground = True
        wrd.rp_stereo = False
        wrd.rp_greasepencil = False
        wrd.rp_voxelgi = False
        wrd.rp_render_to_texture = False
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'None'
        wrd.rp_compositornodes = False
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = False
        wrd.rp_ssr = False
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'
    elif preset == 'Grease Pencil':
        wrd.rp_renderer = 'Forward'
        wrd.arm_material_model = 'Restricted'
        wrd.rp_shadowmap = 'None'
        wrd.rp_translucency_state = 'Off'
        wrd.rp_overlays_state = 'Off'
        wrd.rp_decals_state = 'Off'
        wrd.rp_sss_state = 'Off'
        wrd.rp_hdr = False
        wrd.rp_world = False
        wrd.rp_clearbackground = True
        wrd.rp_stereo = False
        wrd.rp_greasepencil = True
        wrd.rp_render_to_texture = False
        wrd.rp_supersampling = '1'
        wrd.rp_antialiasing = 'None'
        wrd.rp_compositornodes = False
        wrd.rp_volumetriclight = False
        wrd.rp_ssao = False
        wrd.rp_ssr = False
        wrd.rp_dfrs = False
        wrd.rp_dfao = False
        wrd.rp_dfgi = False
        wrd.rp_bloom = False
        wrd.rp_eyeadapt = False
        wrd.rp_rendercapture = False
        wrd.rp_motionblur = 'None'

    updating_preset = False
    set_renderpath(self, context)

def set_renderpath(self, context):
    global updating_preset
    if updating_preset == True:
        return
    # assets.invalidate_compiled_data(self, context)
    assets.invalidate_shader_cache(self, context)
    make_renderer(bpy.data.worlds['Arm'])

def make_renderer(wrd):
    global group
    global nodes
    global links

    if bpy.data.filepath.endswith('arm_data.blend'): # Prevent load in library itself
        return

    if wrd.rp_renderer == 'Forward':
        load_library('forward_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_forward(wrd)
    elif wrd.rp_renderer == 'Deferred':
        load_library('deferred_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_deferred(wrd)
    elif wrd.rp_renderer == 'Deferred Plus':
        load_library('deferred_plus_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_deferred_plus(wrd)

def relink(start_node, next_node):
    if len(nodes[start_node].inputs[0].links) > 0:
        n = nodes[start_node].inputs[0].links[0].from_node
        l = n.outputs[0].links[0]
        links.remove(l)
        links.new(n.outputs[0], nodes[next_node].inputs[0])

def make_forward(wrd):

    nodes['Begin'].inputs[1].default_value = wrd.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(wrd.rp_supersampling)

    if wrd.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(wrd.rp_shadowmap)
    else:
        l = nodes['Begin'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Begin'].outputs[0], nodes['Set Target Mesh'].inputs[0])
        relink('Bind Target Mesh SM', 'Draw Meshes Mesh') # No shadowmap bind
        relink('Bind Target Transluc SM', 'Draw Meshes Transluc')

    if wrd.rp_stereo:
        if wrd.rp_shadowmap != 'None':
            links.new(nodes['Bind Target Mesh SM'].outputs[0], nodes['Draw Stereo'].inputs[0])
        else:
            links.new(nodes['Clear Target Mesh'].outputs[0], nodes['Draw Stereo'].inputs[0])
        links.new(nodes['Draw Stereo'].outputs[1], nodes['Draw Meshes Mesh'].inputs[0])

    if wrd.rp_greasepencil:
        if wrd.rp_shadowmap != 'None':
            links.new(nodes['Bind Target Mesh SM'].outputs[0], nodes['Draw Grease Pencil'].inputs[0])
        else:
            links.new(nodes['Clear Target Mesh'].outputs[0], nodes['Draw Grease Pencil'].inputs[0])
        links.new(nodes['Draw Grease Pencil'].outputs[0], nodes['Draw Meshes Mesh'].inputs[0])

    if not wrd.rp_world:
        relink('Draw World', 'Set Target Accum')
        if wrd.rp_clearbackground:
            nodes['Clear Target Mesh'].inputs[1].default_value = True

    if not wrd.rp_render_to_texture:
        links.new(nodes['Framebuffer'].outputs[0], nodes['Set Target Mesh'].inputs[1])
        if wrd.rp_world:
            l = nodes['Draw World'].outputs[0].links[0]
        elif wrd.rp_greasepencil:
            l = nodes['Draw Grease Pencil'].outputs[0].links[0]
        else:
            l = nodes['Draw Meshes Mesh'].outputs[0].links[0]
        links.remove(l)

    if not wrd.rp_translucency:
        relink('Set Target Accum', 'Draw Compositor + FXAA')

    last_node = 'Draw Compositor + FXAA'
    if wrd.rp_antialiasing == 'SMAA':
        pass
    elif wrd.rp_antialiasing == 'TAA':
        pass
    elif wrd.rp_antialiasing == 'FXAA':
        pass
    elif wrd.rp_antialiasing == 'None':
        last_node = 'Draw Compositor'
        relink('Draw Compositor + FXAA', 'Draw Compositor')

    if wrd.rp_overlays:
        links.new(last_node.outputs[0], nodes['Clear Target Overlay'].inputs[0])

def make_deferred(wrd):

    nodes['Begin'].inputs[1].default_value = wrd.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(wrd.rp_supersampling)

    if wrd.rp_voxelgi:
        n = nodes['Image 3D Voxels']
        # if wrd.rp_voxelgi_hdr:
            # n.inputs[4].default_value = 'RGBA64'
        links.new(nodes['Begin'].outputs[0], nodes['Branch Function Voxelize'].inputs[0])
        links.new(nodes['Merge Stages Voxelize'].outputs[0], nodes['Set Target Mesh'].inputs[0])
        res = int(wrd.rp_voxelgi_resolution)
        n.inputs[1].default_value = res
        n.inputs[2].default_value = res
        n.inputs[3].default_value = res
        n = nodes['Set Viewport Voxels']
        n.inputs[1].default_value = res
        n.inputs[2].default_value = res
        links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Indirect'].inputs[4])
        wrd = bpy.data.worlds['Arm']
        if wrd.arm_voxelgi_shadows or wrd.arm_voxelgi_refraction:
            links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Light'].inputs[4])
            links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Light.001'].inputs[4])

    if wrd.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(wrd.rp_shadowmap)
    else:
        l = nodes['Loop Lamps'].outputs[1].links[0]
        links.remove(l)
        links.new(nodes['Loop Lamps'].outputs[1], nodes['Deferred Light'].inputs[0])
        l = nodes['Deferred Light'].inputs[3].links[0] # No shadowmap bind
        links.remove(l)
        l = nodes['Volumetric Light'].inputs[6].links[0]
        links.remove(l)
        relink('Bind Target Transluc SM', 'Draw Meshes Transluc')

    if wrd.rp_volumetriclight:
        links.new(nodes['Deferred Light'].outputs[0], nodes['Volumetric Light'].inputs[0])

    if not wrd.rp_decals:
        relink('Set Target Decal', 'SSAO')

    if not wrd.rp_ssao:
        relink('SSAO', 'Deferred Indirect')        
        l = nodes['Deferred Indirect'].inputs[3].links[0]
        links.remove(l)

    if not wrd.rp_world:
        relink('Draw World', 'Water')
        if wrd.rp_clearbackground:
            nodes['Clear Target Mesh'].inputs[1].default_value = True

    if not wrd.rp_ocean:
        relink('Water', 'Set Target Accum')

    if not wrd.rp_translucency:
        relink('Set Target Accum', 'Bloom')

    if not wrd.rp_bloom:
        relink('Bloom', 'SSS')

    if not wrd.rp_sss:
        relink('SSS', 'SSR')

    if not wrd.rp_ssr:
        relink('SSR', 'Draw Compositor')

    if bpy.data.worlds['Arm'].arm_ssr_half_res:
        links.new(nodes['ssra'].outputs[0], nodes['SSR'].inputs[2])
        links.new(nodes['ssrb'].outputs[0], nodes['SSR'].inputs[3])

    last_node = 'Draw Compositor'
    if not wrd.rp_compositornodes:
        pass

    if wrd.rp_overlays:
        links.new(nodes[last_node].outputs[0], nodes['Clear Target Overlay'].inputs[0])
        last_node = 'Draw Meshes Overlay'
        links.new(nodes[last_node].outputs[0], nodes['SMAA'].inputs[0])

    if wrd.rp_antialiasing == 'SMAA':
        last_node = 'SMAA'
    elif wrd.rp_antialiasing == 'TAA':
        last_node = 'Copy'
        links.new(nodes['SMAA'].outputs[0], nodes['TAA'].inputs[0])
        links.new(nodes['Reroute.019'].outputs[0], nodes['SMAA'].inputs[5])
        links.new(nodes['gbuffer2'].outputs[0], nodes['GBuffer'].inputs[2])
        links.new(nodes['Reroute.014'].outputs[0], nodes['SMAA'].inputs[1])
        # Clear velocity
        relink('Set Target Mesh', 'Set Target Veloc')
        links.new(nodes['Clear Target Veloc'].outputs[0], nodes['Set Target Mesh'].inputs[0])
    elif wrd.rp_antialiasing == 'FXAA':
        last_node = 'FXAA'
        relink('SMAA', 'FXAA')
    elif wrd.rp_antialiasing == 'None':
        last_node = 'Draw Compositor'
        l = nodes['Draw Compositor'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Framebuffer'].outputs[0], nodes['Draw Compositor'].inputs[1])

    if wrd.rp_supersampling == '4':
        links.new(nodes[last_node].outputs[0], nodes['SS Resolve'].inputs[0])
        last_node = 'SS Resolve'
        if wrd.rp_antialiasing == 'SMAA':
            links.new(nodes['Reroute.014'].outputs[0], nodes['SMAA'].inputs[1])
            links.new(nodes['Reroute.014'].outputs[0], nodes['SS Resolve'].inputs[2])
        elif wrd.rp_antialiasing == 'TAA':
            links.new(nodes['Reroute.008'].outputs[0], nodes['TAA'].inputs[1])
            links.new(nodes['Reroute.008'].outputs[0], nodes['SS Resolve'].inputs[2])
        elif wrd.rp_antialiasing == 'FXAA':
            links.new(nodes['Reroute.008'].outputs[0], nodes['FXAA'].inputs[1])
            links.new(nodes['Reroute.008'].outputs[0], nodes['SS Resolve'].inputs[2])
        elif wrd.rp_antialiasing == 'None':
            links.new(nodes['Reroute.008'].outputs[0], nodes['Draw Compositor'].inputs[1])
            links.new(nodes['Reroute.008'].outputs[0], nodes['SS Resolve'].inputs[2])

    if wrd.rp_eyeadapt:
        links.new(nodes[last_node].outputs[0], nodes['Histogram'].inputs[0])
        links.new(nodes['histogram'].outputs[0], nodes['Draw Compositor'].inputs[5])


    if wrd.rp_rendercapture:
        # links.new(nodes[last_node].outputs[0], nodes['CopyCapture'].inputs[0])
        fb = nodes['Framebuffer']
        cc = nodes['CopyCapture']
        cn = nodes['Capture']
        for l in fb.outputs[0].links:
            if l.to_node != cc:
                links.new(cn.outputs[0], l.to_socket)
        if wrd.rp_rendercapture_format == '8bit':
            cn.inputs[4].default_value = 'RGBA32'
        elif wrd.rp_rendercapture_format == '16bit':
            cn.inputs[4].default_value = 'RGBA64'
        elif wrd.rp_rendercapture_format == '32bit':
            cn.inputs[4].default_value = 'RGBA128'

def make_deferred_plus(wrd):
    pass

# Handling node data
def check_default():
    if (bpy.data.node_groups.get('armory_default') == None or bpy.data.filepath == ''): # Old RP nodes can be saved in startup file, reload those when fp is ''
        make_renderer(bpy.data.worlds['Arm'])

def reload_blend_data():
    armory_pbr = bpy.data.node_groups.get('Armory PBR')
    if armory_pbr != None and len(armory_pbr.inputs) == 14:
        armory_pbr.name = 'Armory PBR Old'
        armory_pbr = None
    if armory_pbr == None:
        load_library('Armory PBR')
    check_default()

def load_library(asset_name, rename=None):
    if bpy.data.filepath.endswith('arm_data.blend'): # Prevent load in library itself
        return
    sdk_path = arm.utils.get_sdk_path()
    data_path = sdk_path + '/armory/blender/data/arm_data.blend'
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
