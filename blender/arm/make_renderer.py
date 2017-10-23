import bpy
import arm.nodes_renderpath as nodes_renderpath
import arm.utils
import arm.assets as assets

group = None
nodes = None
links = None

updating_preset = False
first_build = True

def check_default():
    global first_build
    wrd = bpy.data.worlds['Arm']
    if len(wrd.arm_rplist) == 0:
        wrd.arm_rplist.add()
        wrd.arm_rplist_index = 0
        first_build = True
    if first_build == True:
        make_renderer(arm.utils.get_rp())
    first_build = False

def set_preset(self, context, preset):
    global updating_preset
    rpdat = arm.utils.get_rp()
    updating_preset = True

    if preset == 'Low':
        rpdat.rp_renderer = 'Forward'
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'None'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = False
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = False
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
    elif preset == 'Forward':
        rpdat.rp_renderer = 'Forward'
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadowmap = '2048'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'SMAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = True
        rpdat.rp_ssr = True
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = False
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
    elif preset == 'Deferred':
        rpdat.rp_renderer = 'Deferred'
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadowmap = '2048'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'FXAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = True
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = False
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
    elif preset == 'Render Capture':
        rpdat.rp_renderer = 'Deferred'
        rpdat.rp_shadowmap = '8192'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Voxel GI'
        rpdat.rp_voxelgi_resolution = '256'
        rpdat.rp_voxelgi_emission = True
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '2'
        rpdat.rp_antialiasing = 'TAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = True
        rpdat.rp_ssr = True
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = True
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_material_model = 'Full'
        rpdat.arm_pcss_state = 'On'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'OrenNayar'
    elif preset == 'Deferred Plus':
        rpdat.rp_renderer = 'Deferred Plus'
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadowmap = '4096'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'TAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = True
        rpdat.rp_ssr = True
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = False
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
    elif preset == 'VR Low':
        rpdat.rp_renderer = 'Forward'
        rpdat.arm_material_model = 'Mobile'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = True
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'None'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = False
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = False
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Point'
        rpdat.arm_diffuse_model = 'Lambert'
    elif preset == 'Mobile Low':
        rpdat.rp_renderer = 'Forward'
        rpdat.arm_material_model = 'Mobile'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'Clear'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'None'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = False
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = False
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Point'
        rpdat.arm_diffuse_model = 'Lambert'
    elif preset == 'Grease Pencil':
        rpdat.rp_renderer = 'Forward'
        rpdat.arm_material_model = 'Solid'
        rpdat.rp_shadowmap = 'None'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = True
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'None'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = False
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = False
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
    elif preset == 'Max':
        rpdat.rp_renderer = 'Deferred'
        rpdat.rp_shadowmap = '8192'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Voxel GI'
        rpdat.rp_voxelgi_resolution = '128'
        rpdat.arm_voxelgi_revoxelize = True
        rpdat.arm_voxelgi_camera = True
        rpdat.rp_voxelgi_emission = False
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'TAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssao = True
        rpdat.rp_ssr = True
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_rendercapture = True
        rpdat.rp_motionblur = 'None'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_material_model = 'Full'
        rpdat.arm_pcss_state = 'On'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'OrenNayar'

    updating_preset = False
    set_renderpath(self, context)

def set_renderpath(self, context):
    global updating_preset
    if updating_preset == True:
        return
    # assets.invalidate_compiled_data(self, context)
    assets.invalidate_shader_cache(self, context)
    make_renderer(arm.utils.get_rp())

def make_renderer(rpdat):
    global group
    global nodes
    global links

    if bpy.data.filepath.endswith('arm_data.blend'): # Prevent load in library itself
        return

    if rpdat.rp_renderer == 'Forward':
        load_library('forward_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_forward(rpdat)
    elif rpdat.rp_renderer == 'Deferred':
        load_library('deferred_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_deferred(rpdat)
    elif rpdat.rp_renderer == 'Deferred Plus':
        load_library('deferred_plus_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_deferred_plus(rpdat)

def relink(start_node, next_node):
    if len(nodes[start_node].inputs[0].links) > 0:
        n = nodes[start_node].inputs[0].links[0].from_node
        l = n.outputs[0].links[0]
        links.remove(l)
        links.new(n.outputs[0], nodes[next_node].inputs[0])

def make_forward(rpdat):

    nodes['Begin'].inputs[1].default_value = rpdat.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(rpdat.rp_supersampling)

    if not rpdat.rp_hdr:
        nodes['lbuf'].inputs[4].default_value = 'RGBA32'

    if rpdat.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(rpdat.rp_shadowmap)
    else:
        l = nodes['Begin'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Begin'].outputs[0], nodes['Set Target Mesh'].inputs[0])
        relink('Bind Target Mesh SM', 'Draw Meshes Mesh') # No shadowmap bind
        relink('Bind Target Transluc SM', 'Draw Meshes Transluc')

    if rpdat.rp_stereo:
        if rpdat.rp_shadowmap != 'None':
            links.new(nodes['Bind Target Mesh SM'].outputs[0], nodes['Draw Stereo'].inputs[0])
        else:
            links.new(nodes['Clear Target Mesh'].outputs[0], nodes['Draw Stereo'].inputs[0])
        links.new(nodes['Draw Stereo'].outputs[1], nodes['Draw Meshes Mesh'].inputs[0])

    if rpdat.rp_greasepencil:
        if rpdat.rp_shadowmap != 'None':
            links.new(nodes['Bind Target Mesh SM'].outputs[0], nodes['Draw Grease Pencil'].inputs[0])
        else:
            links.new(nodes['Clear Target Mesh'].outputs[0], nodes['Draw Grease Pencil'].inputs[0])
        links.new(nodes['Draw Grease Pencil'].outputs[0], nodes['Draw Meshes Mesh'].inputs[0])

    if rpdat.rp_background != 'World':
        relink('Draw World', 'Set Target Accum')
        if rpdat.rp_background == 'Clear':
            nodes['Clear Target Mesh'].inputs[1].default_value = True

    if not rpdat.rp_render_to_texture:
        links.new(nodes['Framebuffer'].outputs[0], nodes['Set Target Mesh'].inputs[1])
        if rpdat.rp_background == 'World':
            l = nodes['Draw World'].outputs[0].links[0]
        elif rpdat.rp_greasepencil:
            l = nodes['Draw Grease Pencil'].outputs[0].links[0]
        else:
            l = nodes['Draw Meshes Mesh'].outputs[0].links[0]
        links.remove(l)

    if not rpdat.rp_translucency:
        relink('Set Target Accum', 'Draw Compositor + FXAA')

    last_node = 'Draw Compositor + FXAA'
    if rpdat.rp_antialiasing == 'SMAA':
        pass
    elif rpdat.rp_antialiasing == 'TAA':
        pass
    elif rpdat.rp_antialiasing == 'FXAA':
        pass
    elif rpdat.rp_antialiasing == 'None':
        last_node = 'Draw Compositor'
        relink('Draw Compositor + FXAA', 'Draw Compositor')

    if rpdat.rp_overlays:
        links.new(last_node.outputs[0], nodes['Clear Target Overlay'].inputs[0])

    if not rpdat.rp_compositornodes:
        relink(last_node, 'Copy')

def make_deferred(rpdat):

    nodes['Begin'].inputs[1].default_value = rpdat.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(rpdat.rp_supersampling)

    if rpdat.rp_gi == 'Voxel GI':
        n = nodes['Image 3D Voxels']
        if rpdat.rp_voxelgi_hdr:
            n.inputs[4].default_value = 'RGBA64'

        # One lamp only for now - draw shadow map in advance
        links.new(nodes['Begin'].outputs[0], nodes['Set Target SM'].inputs[0])
        links.new(nodes['Draw Meshes SM'].outputs[0], nodes['Branch Function Voxelize'].inputs[0])
        l = nodes['Loop Lamps'].outputs[1].links[0]
        links.remove(l)
        links.new(nodes['Loop Lamps'].outputs[1], nodes['Deferred Light'].inputs[0])
        links.new(nodes['Merge Stages Voxelize'].outputs[0], nodes['Set Target Mesh'].inputs[0])
        res = int(rpdat.rp_voxelgi_resolution)
        n.inputs[1].default_value = res
        n.inputs[2].default_value = res
        n.inputs[3].default_value = int(res * float(rpdat.rp_voxelgi_resolution_z))
        n = nodes['Set Viewport Voxels']
        n.inputs[1].default_value = res
        n.inputs[2].default_value = res
        links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Indirect'].inputs[4])
        if rpdat.arm_voxelgi_shadows or rpdat.arm_voxelgi_refraction:
            links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Light'].inputs[4])
            links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Light.001'].inputs[4])
    elif rpdat.rp_gi == 'Voxel AO':
        n = nodes['Image 3D Voxels']
        n.inputs[4].default_value = 'R8'
        links.new(nodes['Begin'].outputs[0], nodes['Branch Function Voxelize'].inputs[0])
        links.new(nodes['Merge Stages Voxelize'].outputs[0], nodes['Set Target Mesh'].inputs[0])
        res = int(rpdat.rp_voxelgi_resolution)
        n.inputs[1].default_value = res
        n.inputs[2].default_value = res
        n.inputs[3].default_value = int(res * float(rpdat.rp_voxelgi_resolution_z))
        n = nodes['Set Viewport Voxels']
        n.inputs[1].default_value = res
        n.inputs[2].default_value = res
        links.new(nodes['Image 3D Voxels'].outputs[0], nodes['Deferred Indirect'].inputs[4])

    if rpdat.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(rpdat.rp_shadowmap)
    else:
        l = nodes['Loop Lamps'].outputs[1].links[0]
        links.remove(l)
        links.new(nodes['Loop Lamps'].outputs[1], nodes['Deferred Light'].inputs[0])
        l = nodes['Deferred Light'].inputs[3].links[0] # No shadowmap bind
        links.remove(l)
        l = nodes['Volumetric Light'].inputs[6].links[0]
        links.remove(l)
        relink('Bind Target Transluc SM', 'Draw Meshes Transluc')

    if rpdat.rp_volumetriclight:
        links.new(nodes['Deferred Light'].outputs[0], nodes['Volumetric Light'].inputs[0])

    if not rpdat.rp_decals:
        relink('Set Target Decal', 'SSAO')

    if not rpdat.rp_ssao:
        relink('SSAO', 'Deferred Indirect')        
        l = nodes['Deferred Indirect'].inputs[3].links[0]
        links.remove(l)

    if rpdat.rp_background != 'World':
        relink('Draw World', 'Water')
        if rpdat.rp_background == 'Clear':
            nodes['Clear Target Mesh'].inputs[1].default_value = True

    if not rpdat.rp_ocean:
        relink('Water', 'Draw Meshes Blend')

    if rpdat.rp_blending_state == 'Off':
        relink('Draw Meshes Blend', 'Set Target Accum')

    if not rpdat.rp_translucency:
        relink('Set Target Accum', 'Bloom')

    if not rpdat.rp_bloom:
        relink('Bloom', 'SSS')

    if not rpdat.rp_sss:
        relink('SSS', 'SSR')

    if not rpdat.rp_ssr:
        relink('SSR', 'Draw Compositor')

    if rpdat.arm_ssr_half_res:
        links.new(nodes['ssra'].outputs[0], nodes['SSR'].inputs[2])
        links.new(nodes['ssrb'].outputs[0], nodes['SSR'].inputs[3])

    last_node = 'Draw Compositor'
    if not rpdat.rp_compositornodes:
        pass

    if rpdat.rp_overlays:
        links.new(nodes[last_node].outputs[0], nodes['Clear Target Overlay'].inputs[0])
        last_node = 'Draw Meshes Overlay'
        links.new(nodes[last_node].outputs[0], nodes['SMAA'].inputs[0])

    if rpdat.rp_antialiasing == 'SMAA':
        last_node = 'SMAA'
    elif rpdat.rp_antialiasing == 'TAA':
        last_node = 'Copy'
        links.new(nodes['SMAA'].outputs[0], nodes['TAA'].inputs[0])
        links.new(nodes['Reroute.019'].outputs[0], nodes['SMAA'].inputs[5])
        links.new(nodes['gbuffer2'].outputs[0], nodes['GBuffer'].inputs[2])
        links.new(nodes['Reroute.014'].outputs[0], nodes['SMAA'].inputs[1])
        # Clear velocity
        relink('Set Target Mesh', 'Set Target Veloc')
        links.new(nodes['Clear Target Veloc'].outputs[0], nodes['Set Target Mesh'].inputs[0])
    elif rpdat.rp_antialiasing == 'FXAA':
        last_node = 'FXAA'
        relink('SMAA', 'FXAA')
    elif rpdat.rp_antialiasing == 'None':
        last_node = 'Draw Compositor'
        l = nodes['Draw Compositor'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Framebuffer'].outputs[0], nodes['Draw Compositor'].inputs[1])

    if rpdat.rp_supersampling == '4':
        links.new(nodes[last_node].outputs[0], nodes['SS Resolve'].inputs[0])
        last_node = 'SS Resolve'
        if rpdat.rp_antialiasing == 'SMAA':
            links.new(nodes['Reroute.014'].outputs[0], nodes['SMAA'].inputs[1])
            links.new(nodes['Reroute.014'].outputs[0], nodes['SS Resolve'].inputs[2])
        elif rpdat.rp_antialiasing == 'TAA':
            links.new(nodes['Reroute.008'].outputs[0], nodes['TAA'].inputs[1])
            links.new(nodes['Reroute.008'].outputs[0], nodes['SS Resolve'].inputs[2])
        elif rpdat.rp_antialiasing == 'FXAA':
            links.new(nodes['Reroute.008'].outputs[0], nodes['FXAA'].inputs[1])
            links.new(nodes['Reroute.008'].outputs[0], nodes['SS Resolve'].inputs[2])
        elif rpdat.rp_antialiasing == 'None':
            links.new(nodes['Reroute.008'].outputs[0], nodes['Draw Compositor'].inputs[1])
            links.new(nodes['Reroute.008'].outputs[0], nodes['SS Resolve'].inputs[2])

    if rpdat.rp_eyeadapt:
        links.new(nodes[last_node].outputs[0], nodes['Histogram'].inputs[0])
        links.new(nodes['histogram'].outputs[0], nodes['Draw Compositor'].inputs[5])


    if rpdat.rp_rendercapture:
        # links.new(nodes[last_node].outputs[0], nodes['CopyCapture'].inputs[0])
        fb = nodes['Framebuffer']
        cc = nodes['CopyCapture']
        cn = nodes['Capture']
        for l in fb.outputs[0].links:
            if l.to_node != cc:
                links.new(cn.outputs[0], l.to_socket)
        wrd = bpy.data.worlds['Arm']
        if wrd.rp_rendercapture_format == '8bit':
            cn.inputs[4].default_value = 'RGBA32'
        elif wrd.rp_rendercapture_format == '16bit':
            cn.inputs[4].default_value = 'RGBA64'
        elif wrd.rp_rendercapture_format == '32bit':
            cn.inputs[4].default_value = 'RGBA128'

def make_deferred_plus(rpdat):
    pass

def reload_blend_data():
    global first_build
    first_build = True
    armory_pbr = bpy.data.node_groups.get('Armory PBR')
    if armory_pbr != None and len(armory_pbr.inputs) == 14:
        armory_pbr.name = 'Armory PBR Old'
        armory_pbr = None
    if armory_pbr == None:
        load_library('Armory PBR')

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
