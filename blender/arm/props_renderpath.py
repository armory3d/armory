import os
import shutil
import arm.assets as assets
import arm.utils
import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

def update_preset(self, context):
    rpdat = arm.utils.get_rp()
    if self.rp_preset == 'Low':
        rpdat.rp_renderer = 'Forward'
        rpdat.rp_depthprepass = False
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_shadowmap_cascades = '1'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'Off'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'Off'
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Linear'
        rpdat.arm_diffuse_model = 'Lambert'
        rpdat.arm_radiance = False
        rpdat.arm_radiance_sky = False
    elif self.rp_preset == 'Forward':
        rpdat.rp_renderer = 'Forward'
        rpdat.rp_depthprepass = True
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_shadowmap_cascades = '4'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Auto'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'SMAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'SSAO'
        rpdat.rp_ssr = True
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
        rpdat.arm_radiance = True
        rpdat.arm_radiance_sky = True
    elif self.rp_preset == 'Deferred':
        rpdat.rp_renderer = 'Deferred'
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_shadowmap_cascades = '4'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Auto'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'FXAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'SSAO'
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
        rpdat.arm_radiance = True
        rpdat.arm_radiance_sky = True
    elif self.rp_preset == 'Max (Render)':
        rpdat.rp_renderer = 'Deferred'
        rpdat.rp_shadowmap = '8192'
        rpdat.rp_shadowmap_cascades = '1'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Auto'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Voxel GI'
        rpdat.rp_voxelgi_resolution = '256'
        rpdat.rp_voxelgi_emission = True
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '2'
        rpdat.rp_antialiasing = 'TAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'RTGI'
        rpdat.rp_ssr = True
        rpdat.arm_ssr_half_res = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = True
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_material_model = 'Full'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'OrenNayar'
        rpdat.arm_radiance = True
        rpdat.arm_radiance_sky = True
    elif self.rp_preset == 'VR':
        rpdat.rp_renderer = 'Forward'
        rpdat.rp_depthprepass = False
        rpdat.arm_material_model = 'Mobile'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_shadowmap_cascades = '1'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = True
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'Off'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'Off'
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Point'
        rpdat.arm_diffuse_model = 'Lambert'
        rpdat.arm_radiance = True
        rpdat.arm_radiance_sky = True
    elif self.rp_preset == 'Mobile':
        rpdat.rp_renderer = 'Forward'
        rpdat.rp_depthprepass = False
        rpdat.arm_material_model = 'Mobile'
        rpdat.rp_shadowmap = '1024'
        rpdat.rp_shadowmap_cascades = '1'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'Clear'
        rpdat.rp_stereo = False
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'Off'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'Off'
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Linear'
        rpdat.arm_diffuse_model = 'Lambert'
        rpdat.arm_radiance = False
        rpdat.arm_radiance_sky = False
    elif self.rp_preset == 'Max (Game)':
        rpdat.rp_renderer = 'Deferred'
        rpdat.rp_shadowmap = '4096'
        rpdat.rp_shadowmap_cascades = '4'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Auto'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Voxel AO'
        rpdat.rp_voxelgi_resolution = '128'
        rpdat.arm_voxelgi_revoxelize = False
        rpdat.arm_voxelgi_camera = False
        rpdat.rp_voxelgi_emission = False
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'TAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'RTGI'
        rpdat.arm_ssrs = False
        rpdat.rp_ssr = True
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = True
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_material_model = 'Full'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_diffuse_model = 'Lambert'
        rpdat.arm_radiance = True
        rpdat.arm_radiance_sky = True
    elif self.rp_preset == 'Lightmap':
        rpdat.rp_renderer = 'Forward'
        rpdat.rp_depthprepass = False
        rpdat.arm_material_model = 'Solid'
        rpdat.rp_shadowmap = 'Off'
        rpdat.rp_shadowmap_cascades = '1'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        # rpdat.rp_greasepencil = False
        rpdat.rp_gi = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'Off'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'Off'
        rpdat.rp_ssr = False
        rpdat.rp_dfrs = False
        rpdat.rp_dfao = False
        rpdat.rp_dfgi = False
        rpdat.rp_bloom = False
        rpdat.rp_eyeadapt = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Linear'
        rpdat.arm_diffuse_model = 'Lambert'
        rpdat.arm_radiance = False
        rpdat.arm_radiance_sky = False
    update_renderpath(self, context)

def update_renderpath(self, context):
    if assets.invalidate_enabled == False:
        return
    assets.invalidate_shader_cache(self, context)
    bpy.data.worlds['Arm'].arm_recompile = True

def udpate_shadowmap_cascades(self, context):
    bpy.data.worlds['Arm'].arm_recompile = True
    update_renderpath(self, context)

def update_material_model(self, context):
    assets.invalidate_shader_cache(self, context)
    update_renderpath(self, context)

def update_translucency_state(self, context):
    if self.rp_translucency_state == 'On':
        self.rp_translucency = True
    elif self.rp_translucency_state == 'Off':
        self.rp_translucency = False
    else: # Auto - updates rp at build time if translucent mat is used
        return
    update_renderpath(self, context)

def update_decals_state(self, context):
    if self.rp_decals_state == 'On':
        self.rp_decals = True
    elif self.rp_decals_state == 'Off':
        self.rp_decals = False
    else: # Auto - updates rp at build time if decal mat is used
        return
    update_renderpath(self, context)

def update_overlays_state(self, context):
    if self.rp_overlays_state == 'On':
        self.rp_overlays = True
    elif self.rp_overlays_state == 'Off':
        self.rp_overlays = False
    else: # Auto - updates rp at build time if x-ray mat is used
        return
    update_renderpath(self, context)

def update_blending_state(self, context):
    if self.rp_blending_state == 'On':
        self.rp_blending = True
    elif self.rp_blending_state == 'Off':
        self.rp_blending = False
    else: # Auto - updates rp at build time if blending mat is used
        return
    update_renderpath(self, context)

def update_sss_state(self, context):
    if self.rp_sss_state == 'On':
        self.rp_sss = True
    elif self.rp_sss_state == 'Off':
        self.rp_sss = False
    else: # Auto - updates rp at build time if sss mat is used
        return
    update_renderpath(self, context)

class ArmRPListItem(bpy.types.PropertyGroup):
    name = StringProperty(
           name="Name",
           description="A name for this item",
           default="Path")

    rp_driver_list = CollectionProperty(type=bpy.types.PropertyGroup)
    rp_driver = StringProperty(name="Driver", default="Armory", update=assets.invalidate_compiled_data)
    rp_renderer = EnumProperty(
        items=[('Forward', 'Forward', 'Forward'),
               ('Deferred', 'Deferred', 'Deferred'),
               # ('Deferred Plus', 'Deferred Plus', 'Deferred Plus'),
               # ('Pathtracer', 'Pathtracer', 'Pathtracer'),
               ],
        name="Renderer", description="Renderer type", default='Deferred', update=update_renderpath)
    rp_depthprepass = BoolProperty(name="Depth Prepass", description="Depth Prepass for mesh context", default=True, update=update_renderpath)
    rp_hdr = BoolProperty(name="HDR", description="Render in HDR Space", default=True, update=update_renderpath)
    rp_render_to_texture = BoolProperty(name="Post Process", description="Render scene to texture for further processing", default=True, update=update_renderpath)
    rp_background = EnumProperty(
      items=[('World', 'World', 'World'),
             ('Clear', 'Clear', 'Clear'),
             ('Off', 'No Clear', 'Off'),
      ],
      name="Background", description="Background type", default='World', update=update_renderpath)    
    arm_irradiance = BoolProperty(name="Irradiance", description="Generate spherical harmonics", default=True, update=assets.invalidate_shader_cache)
    arm_radiance = BoolProperty(name="Radiance", description="Generate radiance textures", default=True, update=assets.invalidate_shader_cache)
    arm_radiance_size = EnumProperty(
        items=[('512', '512', '512'),
               ('1024', '1024', '1024'), 
               ('2048', '2048', '2048')],
        name="", description="Prefiltered map size", default='1024', update=assets.invalidate_envmap_data)
    arm_radiance_sky = BoolProperty(name="Sky Radiance", default=True, update=assets.invalidate_shader_cache)
    rp_autoexposure = BoolProperty(name="Auto Exposure", description="Adjust exposure based on luminance", default=False, update=update_renderpath)
    rp_compositornodes = BoolProperty(name="Compositor", description="Draw compositor nodes", default=True, update=update_renderpath)
    rp_shadowmap = EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('512', '512', '512'),
               ('1024', '1024', '1024'),
               ('2048', '2048', '2048'),
               ('4096', '4096', '4096'),
               ('8192', '8192', '8192'),
               ('16384', '16384', '16384'),],
        name="Shadow Map", description="Shadow map resolution", default='1024', update=update_renderpath)
    rp_shadowmap_cascades = EnumProperty(
        items=[('1', '1', '1'),
               ('2', '2', '2'),
               # ('3', '3', '3'),
               ('4', '4', '4')],
        name="Cascades", description="Shadow map cascades", default='4', update=udpate_shadowmap_cascades)
    arm_pcfsize = FloatProperty(name="PCF Size", description="Filter size", default=1.0)
    rp_supersampling = EnumProperty(
        items=[('1', '1', '1'),
               ('1.5', '1.5', '1.5'),
               ('2', '2', '2'),
               ('4', '4', '4')],
        name="Super Sampling", description="Screen resolution multiplier", default='1', update=update_renderpath)
    rp_antialiasing = EnumProperty(
        items=[('Off', 'No AA', 'Off'),
               ('FXAA', 'FXAA', 'FXAA'),
               ('SMAA', 'SMAA', 'SMAA'),
               ('TAA', 'TAA', 'TAA')],
        name="Anti Aliasing", description="Post-process anti aliasing technique", default='SMAA', update=update_renderpath)
    rp_volumetriclight = BoolProperty(name="Volumetric Light", description="Use volumetric lighting", default=False, update=update_renderpath)
    rp_ssr = BoolProperty(name="SSR", description="Screen space reflections", default=False, update=update_renderpath)
    rp_ssgi = EnumProperty(
        items=[('Off', 'No AO', 'Off'),
               ('SSAO', 'SSAO', 'Screen space ambient occlusion'),
               ('RTAO', 'RTAO', 'Ray-traced ambient occlusion'),
               ('RTGI', 'RTGI', 'Ray-traced global illumination')
               ],
        name="SSGI", description="Screen space global illumination", default='SSAO', update=update_renderpath)
    rp_dfao = BoolProperty(name="DFAO", description="Distance field ambient occlusion", default=False)
    rp_dfrs = BoolProperty(name="DFRS", description="Distance field ray-traced shadows", default=False)
    rp_dfgi = BoolProperty(name="DFGI", description="Distance field global illumination", default=False)
    rp_bloom = BoolProperty(name="Bloom", description="Bloom processing", default=False, update=update_renderpath)
    rp_eyeadapt = BoolProperty(name="Eye Adaptation", description="Auto-exposure based on histogram", default=False, update=update_renderpath)
    rp_motionblur = EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Camera', 'Camera', 'Camera'),
               ('Object', 'Object', 'Object')],
        name="Motion Blur", description="Velocity buffer is used for object based motion blur", default='Off', update=update_renderpath)
    rp_translucency = BoolProperty(name="Translucency", description="Current render-path state", default=False)
    rp_translucency_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Translucency", description="Order independent translucency", default='Auto', update=update_translucency_state)
    rp_decals = BoolProperty(name="Decals", description="Current render-path state", default=False)
    rp_decals_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Decals", description="Decals pass", default='Auto', update=update_decals_state)
    rp_overlays = BoolProperty(name="Overlays", description="Current render-path state", default=False)
    rp_overlays_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Overlays", description="X-Ray pass", default='Auto', update=update_overlays_state)
    rp_sss = BoolProperty(name="SSS", description="Current render-path state", default=False)
    rp_sss_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="SSS", description="Sub-surface scattering pass", default='Auto', update=update_sss_state)
    rp_blending = BoolProperty(name="Blending", description="Current render-path state", default=False)
    rp_blending_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="Blending", description="Blending pass", default='Auto', update=update_blending_state)
    rp_stereo = BoolProperty(name="VR", description="Stereo rendering", default=False, update=update_renderpath)
    rp_greasepencil = BoolProperty(name="Grease Pencil", description="Render Grease Pencil data", default=False, update=update_renderpath)
    rp_ocean = BoolProperty(name="Ocean", description="Ocean pass", default=False, update=update_renderpath)
    
    rp_gi = EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Voxel GI', 'Voxel GI', 'Voxel GI'),
               ('Voxel AO', 'Voxel AO', 'Voxel AO')
               ],
        name="Global Illumination", description="Dynamic global illumination", default='Off', update=update_renderpath)
    rp_voxelgi_resolution = EnumProperty(
        items=[('32', '32', '32'),
               ('64', '64', '64'),
               ('128', '128', '128'),
               ('256', '256', '256'),
               ('512', '512', '512')],
        name="Resolution", description="3D texture resolution", default='128', update=update_renderpath)
    rp_voxelgi_resolution_z = EnumProperty(
        items=[('1.0', '1.0', '1.0'),
               ('0.5', '0.5', '0.5'),
               ('0.25', '0.25', '0.25')],
        name="Resolution Z", description="3D texture z resolution multiplier", default='1.0', update=update_renderpath)
    arm_clouds = BoolProperty(name="Clouds", default=False, update=assets.invalidate_shader_cache)
    arm_soft_shadows = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Soft Shadows", description="Soft shadows with variable penumbra (spot and non-cascaded sun light supported)", default='Off', update=assets.invalidate_shader_cache)
    arm_soft_shadows_penumbra = IntProperty(name="Penumbra", description="Variable penumbra scale", default=1, min=0, max=10, update=assets.invalidate_shader_cache)
    arm_soft_shadows_distance = FloatProperty(name="Distance", description="Variable penumbra distance", default=1.0, min=0, max=10, update=assets.invalidate_shader_cache)
    arm_ssrs = BoolProperty(name="SSRS", description="Screen-space ray-traced shadows", default=False, update=assets.invalidate_shader_cache)
    arm_texture_filter = EnumProperty(
        items=[('Anisotropic', 'Anisotropic', 'Anisotropic'),
               ('Linear', 'Linear', 'Linear'), 
               ('Point', 'Closest', 'Point'), 
               ('Manual', 'Manual', 'Manual')],
        name="Texture Filtering", description="Set Manual to honor interpolation setting on Image Texture node", default='Anisotropic')
    arm_material_model = EnumProperty(
        items=[('Full', 'Full', 'Full'),
               ('Mobile', 'Mobile', 'Mobile'),
               ('Solid', 'Solid', 'Solid'),
               ],
        name="Materials", description="Material builder", default='Full', update=update_material_model)
    arm_diffuse_model = EnumProperty(
        items=[('Lambert', 'Lambert', 'Lambert'),
               ('OrenNayar', 'OrenNayar', 'OrenNayar'),
               ],
        name="Diffuse", description="Diffuse model", default='Lambert', update=assets.invalidate_shader_cache)
    arm_rp_displacement = EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Vertex', 'Vertex', 'Vertex'),
               ('Tessellation', 'Tessellation', 'Tessellation')],
        name="Displacement", description="Enable material displacement", default='Vertex', update=assets.invalidate_shader_cache)
    arm_tess_mesh_inner = IntProperty(name="Inner", description="Inner tessellation level", default=7)
    arm_tess_mesh_outer = IntProperty(name="Outer", description="Outer tessellation level", default=7)
    arm_tess_shadows_inner = IntProperty(name="Inner", description="Inner tessellation level", default=7)
    arm_tess_shadows_outer = IntProperty(name="Outer", description="Outer tessellation level", default=7)
    arm_rp_resolution = EnumProperty(
        items=[('Display', 'Display', 'Display'),
               ('Custom', 'Custom', 'Custom')],
        name="Resolution", description="Resolution to perform rendering at", default='Display', update=update_renderpath)
    arm_rp_resolution_size = IntProperty(name="Size", description="Resolution height in pixels(for example 720p), width is auto-fit to preserve aspect ratio", default=720, min=0, update=update_renderpath)
    arm_rp_resolution_filter = EnumProperty(
        items=[('Linear', 'Linear', 'Linear'), 
               ('Point', 'Closest', 'Point')],
        name="Filter", description="Scaling filter", default='Linear')
    rp_dynres = BoolProperty(name="Dynamic Resolution", description="Dynamic resolution scaling for performance", default=False, update=update_renderpath)
    arm_ssr_half_res = BoolProperty(name="Half Res", description="Trace in half resolution", default=True, update=update_renderpath)
    rp_ssr_z_only = BoolProperty(name="Z Only", description="Trace in Z axis only", default=False, update=update_renderpath)
    rp_voxelgi_hdr = BoolProperty(name="HDR Voxels", description="Store voxels in RGBA64 instead of RGBA32", default=False, update=update_renderpath)
    rp_voxelgi_relight = BoolProperty(name="Relight", description="Relight voxels when light is moved", default=True, update=update_renderpath)
    arm_voxelgi_dimensions = FloatProperty(name="Dimensions", description="Voxelization bounds",default=16, update=assets.invalidate_shader_cache)
    arm_voxelgi_revoxelize = BoolProperty(name="Revoxelize", description="Revoxelize scene each frame", default=False, update=assets.invalidate_shader_cache)
    arm_voxelgi_temporal = BoolProperty(name="Temporal Filter", description="Use temporal filtering to stabilize voxels", default=False, update=assets.invalidate_shader_cache)
    arm_voxelgi_bounces = EnumProperty(
        items=[('1', '1', '1'),
               ('2', '2', '2')],
        name="Bounces", description="Trace multiple light bounces", default='1', update=update_renderpath)
    arm_voxelgi_camera = BoolProperty(name="Dynamic Camera", description="Use camera as voxelization origin", default=False, update=assets.invalidate_shader_cache)
    # arm_voxelgi_anisotropic = BoolProperty(name="Anisotropic", description="Use anisotropic voxels", default=False, update=update_renderpath)
    arm_voxelgi_shadows = BoolProperty(name="Trace Shadows", description="Use voxels to render shadows", default=False, update=update_renderpath)
    arm_voxelgi_refraction = BoolProperty(name="Trace Refraction", description="Use voxels to render refraction", default=False, update=update_renderpath)
    arm_samples_per_pixel = EnumProperty(
        items=[('1', '1', '1'),
               ('2', '2', '2'),
               ('4', '4', '4'),
               ('8', '8', '8'),
               ('16', '16', '16')],
        name="MSAA", description="Samples per pixel usable for render paths drawing directly to framebuffer", default='1')  
    arm_ssao_half_res = BoolProperty(name="Half Res", description="Trace in half resolution", default=False, update=assets.invalidate_shader_cache)

    arm_voxelgi_diff = FloatProperty(name="Diffuse", description="", default=3.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_cones = EnumProperty(
        items=[('9', '9', '9'),
               ('5', '5', '5'),
               ('3', '3', '3'),
               ('1', '1', '1'),
               ],
        name="Cones", description="Number of cones to trace", default='5', update=assets.invalidate_shader_cache)
    arm_voxelgi_spec = FloatProperty(name="Specular", description="", default=1.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_occ = FloatProperty(name="Occlusion", description="", default=1.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_env = FloatProperty(name="Env Map", description="Contribute light from environment map", default=0.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_step = FloatProperty(name="Step", description="Step size", default=1.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_offset = FloatProperty(name="Offset", description="Ray offset", default=1.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_range = FloatProperty(name="Range", description="Maximum range", default=2.0, update=assets.invalidate_shader_cache)
    arm_sss_width = FloatProperty(name="Width", description="SSS blur strength", default=1.0, update=assets.invalidate_shader_cache)
    arm_clouds_density = FloatProperty(name="Density", default=1.0, min=0.0, max=1.0, update=assets.invalidate_shader_cache)
    arm_clouds_size = FloatProperty(name="Size", default=1.0, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    arm_clouds_lower = FloatProperty(name="Lower", default=2.0, min=1.0, max=10.0, update=assets.invalidate_shader_cache)
    arm_clouds_upper = FloatProperty(name="Upper", default=3.5, min=1.0, max=10.0, update=assets.invalidate_shader_cache)
    arm_clouds_wind = FloatVectorProperty(name="Wind", default=[0.2, 0.06], size=2, update=assets.invalidate_shader_cache)
    arm_clouds_secondary = FloatProperty(name="Secondary", default=0.0, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    arm_clouds_precipitation = FloatProperty(name="Precipitation", default=1.0, min=0.0, max=2.0, update=assets.invalidate_shader_cache)
    arm_clouds_eccentricity = FloatProperty(name="Eccentricity", default=0.6, min=0.0, max=1.0, update=assets.invalidate_shader_cache)
    arm_ocean_base_color = FloatVectorProperty(name="Base Color", size=3, default=[0.1, 0.19, 0.37], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    arm_ocean_water_color = FloatVectorProperty(name="Water Color", size=3, default=[0.6, 0.7, 0.9], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    arm_ocean_level = FloatProperty(name="Level", default=0.0, update=assets.invalidate_shader_cache)
    arm_ocean_amplitude = FloatProperty(name="Amplitude", default=2.5, update=assets.invalidate_shader_cache)
    arm_ocean_height = FloatProperty(name="Height", default=0.6, update=assets.invalidate_shader_cache)
    arm_ocean_choppy = FloatProperty(name="Choppy", default=4.0, update=assets.invalidate_shader_cache)
    arm_ocean_speed = FloatProperty(name="Speed", default=1.5, update=assets.invalidate_shader_cache)
    arm_ocean_freq = FloatProperty(name="Freq", default=0.16, update=assets.invalidate_shader_cache)
    arm_ocean_fade = FloatProperty(name="Fade", default=1.8, update=assets.invalidate_shader_cache)
    arm_ssgi_strength = FloatProperty(name="Strength", default=1.0, update=assets.invalidate_shader_cache)
    arm_ssgi_step = FloatProperty(name="Step", default=2.0, update=assets.invalidate_shader_cache)
    arm_ssgi_max_steps = IntProperty(name="Max Steps", default=8, update=assets.invalidate_shader_cache)
    arm_ssgi_rays = EnumProperty(
        items=[('9', '9', '9'),
               ('5', '5', '5'),
               ],
        name="Rays", description="Number of rays to trace for RTAO/RTGI", default='5', update=assets.invalidate_shader_cache)
    arm_bloom_threshold = FloatProperty(name="Threshold", default=1.0, update=assets.invalidate_shader_cache)
    arm_bloom_strength = FloatProperty(name="Strength", default=3.5, update=assets.invalidate_shader_cache)
    arm_bloom_radius = FloatProperty(name="Radius", default=3.0, update=assets.invalidate_shader_cache)
    arm_motion_blur_intensity = FloatProperty(name="Intensity", default=1.0, update=assets.invalidate_shader_cache)
    arm_ssr_ray_step = FloatProperty(name="Step", default=0.04, update=assets.invalidate_shader_cache)
    arm_ssr_min_ray_step = FloatProperty(name="Step Min", default=0.05, update=assets.invalidate_shader_cache)
    arm_ssr_search_dist = FloatProperty(name="Search", default=5.0, update=assets.invalidate_shader_cache)
    arm_ssr_falloff_exp = FloatProperty(name="Falloff", default=5.0, update=assets.invalidate_shader_cache)
    arm_ssr_jitter = FloatProperty(name="Jitter", default=0.6, update=assets.invalidate_shader_cache)
    arm_volumetric_light_air_turbidity = FloatProperty(name="Air Turbidity", default=1.0, update=assets.invalidate_shader_cache)
    arm_volumetric_light_air_color = FloatVectorProperty(name="Air Color", size=3, default=[1.0, 1.0, 1.0], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    arm_volumetric_light_steps = IntProperty(name="Steps", default=20, min=0, update=assets.invalidate_shader_cache)
    arm_shadowmap_split = FloatProperty(name="Cascade Split", description="Split factor for cascaded shadow maps, higher factor favors detail on close surfaces", default=0.8, update=assets.invalidate_shader_cache)
    arm_shadowmap_bounds = FloatProperty(name="Cascade Bounds", description="Multiply cascade bounds to capture bigger area", default=1.0, update=assets.invalidate_compiled_data)
    arm_autoexposure_strength = FloatProperty(name="Auto Exposure Strength", default=0.7, update=assets.invalidate_shader_cache)
    arm_ssrs_ray_step = FloatProperty(name="Step", default=0.01, update=assets.invalidate_shader_cache)
    # Compositor
    arm_letterbox = BoolProperty(name="Letterbox", default=False, update=assets.invalidate_shader_cache)
    arm_letterbox_size = FloatProperty(name="Size", default=0.1, update=assets.invalidate_shader_cache)
    arm_grain = BoolProperty(name="Film Grain", default=False, update=assets.invalidate_shader_cache)
    arm_grain_strength = FloatProperty(name="Strength", default=2.0, update=assets.invalidate_shader_cache)
    arm_sharpen = BoolProperty(name="Sharpen", default=False, update=assets.invalidate_shader_cache)
    arm_sharpen_strength = FloatProperty(name="Strength", default=0.25, update=assets.invalidate_shader_cache)
    arm_fog = BoolProperty(name="Volumetric Fog", default=False, update=assets.invalidate_shader_cache)
    arm_fog_color = FloatVectorProperty(name="Color", size=3, subtype='COLOR', default=[0.5, 0.6, 0.7], min=0, max=1, update=assets.invalidate_shader_cache)
    arm_fog_amounta = FloatProperty(name="Amount A", default=0.25, update=assets.invalidate_shader_cache)
    arm_fog_amountb = FloatProperty(name="Amount B", default=0.5, update=assets.invalidate_shader_cache)
    arm_tonemap = EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Filmic', 'Filmic', 'Filmic'),
               ('Filmic2', 'Filmic2', 'Filmic2'),
               ('Reinhard', 'Reinhard', 'Reinhard'),
               ('Uncharted', 'Uncharted', 'Uncharted')],
        name='Tonemap', description='Tonemapping operator', default='Filmic', update=assets.invalidate_shader_cache)
    arm_lens_texture = StringProperty(name="Lens Texture", default="")
    arm_fisheye = BoolProperty(name="Fish Eye", default=False, update=assets.invalidate_shader_cache)
    arm_vignette = BoolProperty(name="Vignette", default=False, update=assets.invalidate_shader_cache)
    arm_lensflare = BoolProperty(name="Lens Flare", default=False, update=assets.invalidate_shader_cache)
    arm_lut_texture = StringProperty(name="LUT Texture", description="Color Grading", default="", update=assets.invalidate_shader_cache)
    arm_skin = EnumProperty(
        items=[('GPU (Dual-Quat)', 'GPU (Dual-Quat)', 'GPU (Dual-Quat)'),
               ('GPU (Matrix)', 'GPU (Matrix)', 'GPU (Matrix)'),
               ('CPU', 'CPU', 'CPU'),
               ('Off', 'Off', 'Off')],
        name='Skinning', description='Skinning method', default='GPU (Dual-Quat)', update=assets.invalidate_shader_cache)
    arm_skin_max_bones_auto = BoolProperty(name="Auto Bones", description="Calculate amount of maximum bones based on armatures", default=True, update=assets.invalidate_compiled_data)
    arm_skin_max_bones = IntProperty(name="Max Bones", default=50, min=1, max=3000, update=assets.invalidate_shader_cache)
    arm_particles = EnumProperty(
        items=[('GPU', 'GPU', 'GPU'),
               ('CPU', 'CPU', 'CPU'),
               ('Off', 'Off', 'Off')],
        name='Particles', description='Simulation method', default='GPU', update=assets.invalidate_shader_cache)
    # Material override flags
    arm_culling = BoolProperty(name="Culling", default=True)
    arm_two_sided_area_light = BoolProperty(name="Two-Sided Area Light", description="Emit light from both faces of area plane", default=False, update=assets.invalidate_shader_cache)

class ArmRPList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class ArmRPListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_rplist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        mdata.arm_rplist.add()
        mdata.arm_rplist_index = len(mdata.arm_rplist) - 1
        return{'FINISHED'}


class ArmRPListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_rplist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        mdata = bpy.data.worlds['Arm']
        return len(mdata.arm_rplist) > 0

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        list = mdata.arm_rplist
        index = mdata.arm_rplist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        mdata.arm_rplist_index = index
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ArmRPListItem)
    bpy.utils.register_class(ArmRPList)
    bpy.utils.register_class(ArmRPListNewItem)
    bpy.utils.register_class(ArmRPListDeleteItem)

    bpy.types.World.arm_rplist = CollectionProperty(type=ArmRPListItem)
    bpy.types.World.arm_rplist_index = IntProperty(name="Index for my_list", default=0, update=update_renderpath)

def unregister():
    bpy.utils.unregister_class(ArmRPListItem)
    bpy.utils.unregister_class(ArmRPList)
    bpy.utils.unregister_class(ArmRPListNewItem)
    bpy.utils.unregister_class(ArmRPListDeleteItem)
