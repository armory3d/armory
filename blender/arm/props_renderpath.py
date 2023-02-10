from typing import Optional

import bpy
from bpy.props import *

import arm.assets as assets
import arm.utils

if arm.is_reload(__name__):
    assets = arm.reload_module(assets)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

atlas_sizes = [ ('256', '256', '256'),
                ('512', '512', '512'),
                ('1024', '1024', '1024'),
                ('2048', '2048', '2048'),
                ('4096', '4096', '4096'),
                ('8192', '8192', '8192'),
                ('16384', '16384', '16384'),
                ('32768', '32768', '32768') ]

def atlas_sizes_from_min(min_size: int) -> list:
    """ Create an enum list of atlas sizes from a minimal size """
    sizes = []
    for i in range(len(atlas_sizes)):
        if int(atlas_sizes[i][0]) > min_size:
            sizes.append(atlas_sizes[i])
    return sizes

def update_spot_sun_atlas_size_options(scene: bpy.types.Scene, context: bpy.types.Context) -> list:
    wrd = bpy.data.worlds['Arm']
    if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
        return []
    rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
    return atlas_sizes_from_min(int(rpdat.rp_shadowmap_cascade))

def update_point_atlas_size_options(scene: bpy.types.Scene, context: bpy.types.Context) -> list:
    wrd = bpy.data.worlds['Arm']
    if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
        return []
    rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
    return atlas_sizes_from_min(int(rpdat.rp_shadowmap_cube) * 2)


def update_preset(self, context):
    rpdat = arm.utils.get_rp()
    if rpdat is None:
        rpdat = self.arm_rplist[-1]
    if self.rp_preset == 'Desktop':
        rpdat.rp_renderer = 'Deferred'
        rpdat.arm_material_model = 'Full'
        rpdat.rp_shadows = True
        rpdat.rp_shadowmap_cube = '512'
        rpdat.rp_shadowmap_cascade = '1024'
        rpdat.rp_shadowmap_cascades = '4'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Auto'
        rpdat.rp_depth_texture_state = 'Auto'
        rpdat.rp_draw_order = 'Auto'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_voxels = 'Off'
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'SMAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'SSAO'
        rpdat.arm_ssrs = False
        rpdat.arm_micro_shadowing = False
        rpdat.rp_ssr = False
        rpdat.rp_bloom = False
        rpdat.arm_bloom_quality = 'medium'
        rpdat.arm_bloom_anti_flicker = True
        rpdat.rp_autoexposure = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_irradiance = True
        rpdat.arm_radiance = True
        rpdat.rp_pp = False
    elif self.rp_preset == 'Mobile':
        rpdat.rp_renderer = 'Forward'
        rpdat.rp_depthprepass = False
        rpdat.arm_material_model = 'Mobile'
        rpdat.rp_shadows = True
        rpdat.rp_shadowmap_cube = '256'
        rpdat.rp_shadowmap_cascade = '1024'
        rpdat.rp_shadowmap_cascades = '1'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_depth_texture_state = 'Auto'
        rpdat.rp_draw_order = 'Auto'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'Clear'
        rpdat.rp_stereo = False
        rpdat.rp_voxels = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'Off'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'Off'
        rpdat.arm_ssrs = False
        rpdat.arm_micro_shadowing = False
        rpdat.rp_ssr = False
        rpdat.rp_bloom = False
        rpdat.arm_bloom_quality = 'low'
        rpdat.arm_bloom_anti_flicker = False
        rpdat.rp_autoexposure = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Linear'
        rpdat.arm_irradiance = True
        rpdat.arm_radiance = False
        rpdat.rp_pp = False
    elif self.rp_preset == 'Max':
        rpdat.rp_renderer = 'Deferred'
        rpdat.rp_shadows = True
        rpdat.rp_shadowmap_cube = '2048'
        rpdat.rp_shadowmap_cascade = '4096'
        rpdat.rp_shadowmap_cascades = '4'
        rpdat.rp_translucency_state = 'Auto'
        rpdat.rp_overlays_state = 'Auto'
        rpdat.rp_decals_state = 'Auto'
        rpdat.rp_sss_state = 'Auto'
        rpdat.rp_blending_state = 'Auto'
        rpdat.rp_depth_texture_state = 'Auto'
        rpdat.rp_draw_order = 'Auto'
        rpdat.rp_hdr = True
        rpdat.rp_background = 'World'
        rpdat.rp_stereo = False
        rpdat.rp_voxels = True
        rpdat.rp_voxelgi_resolution = '128'
        rpdat.arm_voxelgi_revoxelize = False
        rpdat.arm_voxelgi_camera = False
        rpdat.rp_voxelgi_emission = False
        rpdat.rp_render_to_texture = True
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'TAA'
        rpdat.rp_compositornodes = True
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'RTAO'
        rpdat.arm_ssrs = False
        rpdat.arm_micro_shadowing = False
        rpdat.rp_ssr = True
        rpdat.rp_ss_refraction = True
        rpdat.arm_ssr_half_res = False
        rpdat.rp_bloom = True
        rpdat.arm_bloom_quality = 'high'
        rpdat.arm_bloom_anti_flicker = True
        rpdat.rp_autoexposure = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_material_model = 'Full'
        rpdat.arm_texture_filter = 'Anisotropic'
        rpdat.arm_irradiance = True
        rpdat.arm_radiance = True
        rpdat.rp_pp = False
    elif self.rp_preset == '2D/Baked':
        rpdat.rp_renderer = 'Forward'
        rpdat.rp_depthprepass = False
        rpdat.arm_material_model = 'Solid'
        rpdat.rp_shadows = False
        rpdat.rp_shadowmap_cube = '512'
        rpdat.rp_shadowmap_cascade = '1024'
        rpdat.rp_shadowmap_cascades = '1'
        rpdat.rp_translucency_state = 'Off'
        rpdat.rp_overlays_state = 'Off'
        rpdat.rp_decals_state = 'Off'
        rpdat.rp_sss_state = 'Off'
        rpdat.rp_blending_state = 'Off'
        rpdat.rp_depth_texture_state = 'Off'
        rpdat.rp_draw_order = 'Auto'
        rpdat.rp_hdr = False
        rpdat.rp_background = 'Clear'
        rpdat.rp_stereo = False
        rpdat.rp_voxels = 'Off'
        rpdat.rp_render_to_texture = False
        rpdat.rp_supersampling = '1'
        rpdat.rp_antialiasing = 'Off'
        rpdat.rp_compositornodes = False
        rpdat.rp_volumetriclight = False
        rpdat.rp_ssgi = 'Off'
        rpdat.arm_ssrs = False
        rpdat.arm_micro_shadowing = False
        rpdat.rp_ssr = False
        rpdat.rp_bloom = False
        rpdat.arm_bloom_quality = 'low'
        rpdat.arm_bloom_anti_flicker = False
        rpdat.rp_autoexposure = False
        rpdat.rp_motionblur = 'Off'
        rpdat.arm_rp_resolution = 'Display'
        rpdat.arm_texture_filter = 'Linear'
        rpdat.arm_irradiance = False
        rpdat.arm_radiance = False
        rpdat.rp_pp = False
    update_renderpath(self, context)

def update_renderpath(self, context):
    if not assets.invalidate_enabled:
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


def update_depth_texture_state(self, context):
    if self.rp_depth_texture_state == 'On':
        self.rp_depth_texture = True
    elif self.rp_depth_texture_state == 'Off':
        self.rp_depth_texture = False
    else: # Auto - updates rp at build time if depth texture mat is used
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
    name: StringProperty(
           name="Name",
           description="A name for this item",
           default="Desktop")

    rp_driver_list: CollectionProperty(type=bpy.types.PropertyGroup)
    rp_driver: StringProperty(name="Driver", default="Armory", update=assets.invalidate_compiled_data)
    rp_renderer: EnumProperty(
        items=[('Forward', 'Forward Clustered', 'Forward'),
               ('Deferred', 'Deferred Clustered', 'Deferred'),
               # ('Raytracer', 'Raytracer', 'Raytracer (Direct3D 12)', 'ERROR', 2),
               ],
        name="Renderer", description="Renderer type", default='Deferred', update=update_renderpath)
    rp_depthprepass: BoolProperty(name="Depth Prepass", description="Depth Prepass for mesh context", default=False, update=update_renderpath)
    rp_hdr: BoolProperty(name="HDR", description="Render in HDR Space", default=True, update=update_renderpath)
    rp_render_to_texture: BoolProperty(name="Post Process", description="Render scene to texture for further processing", default=True, update=update_renderpath)
    rp_background: EnumProperty(
      items=[('World', 'World', 'World'),
             ('Clear', 'Clear', 'Clear'),
             ('Off', 'No Clear', 'Off'),
      ],
      name="Background", description="Background type", default='World', update=update_renderpath)
    arm_irradiance: BoolProperty(name="Irradiance", description="Generate spherical harmonics", default=True, update=assets.invalidate_shader_cache)
    arm_radiance: BoolProperty(name="Radiance", description="Generate radiance textures", default=True, update=assets.invalidate_shader_cache)
    arm_radiance_size: EnumProperty(
        items=[('512', '512', '512'),
               ('1024', '1024', '1024'),
               ('2048', '2048', '2048')],
        name="Map Size", description="Prefiltered map size", default='1024', update=assets.invalidate_envmap_data)
    rp_autoexposure: BoolProperty(name="Auto Exposure", description="Adjust exposure based on luminance", default=False, update=update_renderpath)
    rp_compositornodes: BoolProperty(name="Compositor", description="Draw compositor nodes", default=True, update=update_renderpath)
    rp_shadows: BoolProperty(name="Shadows", description="Enable shadow casting", default=True, update=update_renderpath)
    rp_max_lights: EnumProperty(
        items=[('4', '4', '4'),
               ('8', '8', '8'),
               ('16', '16', '16'),
               ('24', '24', '24'),
               ('32', '32', '32'),
               ('64', '64', '64'),],
        name="Max Lights", description="Max number of lights that can be visible in the screen", default='16')
    rp_max_lights_cluster: EnumProperty(
        items=[('4', '4', '4'),
               ('8', '8', '8'),
               ('16', '16', '16'),
               ('24', '24', '24'),
               ('32', '32', '32'),
               ('64', '64', '64'),],
        name="Max Lights Shadows", description="Max number of rendered shadow maps that can be visible in the screen. Always equal or lower than Max Lights", default='16')
    rp_shadowmap_atlas: BoolProperty(name="Shadow Map Atlasing", description="Group shadow maps of lights of the same type in the same texture", default=False, update=update_renderpath)
    rp_shadowmap_atlas_single_map: BoolProperty(name="Shadow Map Atlas single map", description="Use a single texture for all different light types.", default=False, update=update_renderpath)
    rp_shadowmap_atlas_lod: BoolProperty(name="Shadow Map Atlas LOD (Experimental)", description="When enabled, the size of the shadow map will be determined on runtime based on the distance of the light to the camera", default=False, update=update_renderpath)
    rp_shadowmap_atlas_lod_subdivisions: EnumProperty(
        items=[('2', '2', '2'),
               ('3', '3', '3'),
               ('4', '4', '4'),
               ('5', '5', '5'),
               ('6', '6', '6'),
               ('7', '7', '7'),
               ('8', '8', '8'),],
        name="LOD Subdivisions", description="Number of subdivisions of the default tile size for LOD", default='2', update=update_renderpath)
    rp_shadowmap_atlas_max_size_point: EnumProperty(
        items=update_point_atlas_size_options,
        name="Max Atlas Texture Size Points", description="Sets the limit of the size of the texture.", update=update_renderpath)
    rp_shadowmap_atlas_max_size_spot: EnumProperty(
        items=update_spot_sun_atlas_size_options,
        name="Max Atlas Texture Size Spots", description="Sets the limit of the size of the texture.", update=update_renderpath)
    rp_shadowmap_atlas_max_size_sun: EnumProperty(
        items=update_spot_sun_atlas_size_options,
        name="Max Atlas Texture Size Sun", description="Sets the limit of the size of the texture.", update=update_renderpath)
    rp_shadowmap_atlas_max_size: EnumProperty(
        items=update_spot_sun_atlas_size_options,
        name="Max Atlas Texture Size", description="Sets the limit of the size of the texture.", update=update_renderpath)
    rp_shadowmap_cube: EnumProperty(
        items=[('256', '256', '256'),
               ('512', '512', '512'),
               ('1024', '1024', '1024'),
               ('2048', '2048', '2048'),
               ('4096', '4096', '4096'),],
        name="Cube Size", description="Cube map resolution", default='512', update=update_renderpath)
    rp_shadowmap_cascade: EnumProperty(
        items=[('256', '256', '256'),
               ('512', '512', '512'),
               ('1024', '1024', '1024'),
               ('2048', '2048', '2048'),
               ('4096', '4096', '4096'),
               ('8192', '8192', '8192'),
               ('16384', '16384', '16384'),],
        name="Cascade Size", description="Shadow map resolution", default='1024', update=update_renderpath)
    rp_shadowmap_cascades: EnumProperty(
        items=[('1', '1', '1'),
               ('2', '2', '2'),
               ('4', '4', '4')],
        name="Cascades", description="Shadow map cascades", default='4', update=udpate_shadowmap_cascades)
    arm_pcfsize: FloatProperty(name="PCF Size", description="Filter size", default=1.0)
    rp_supersampling: EnumProperty(
        items=[('1', '1', '1'),
               ('1.5', '1.5', '1.5'),
               ('2', '2', '2'),
               ('4', '4', '4')],
        name="Super Sampling", description="Screen resolution multiplier", default='1', update=update_renderpath)
    rp_antialiasing: EnumProperty(
        items=[('Off', 'No AA', 'Off'),
               ('FXAA', 'FXAA', 'FXAA'),
               ('SMAA', 'SMAA', 'SMAA'),
               ('TAA', 'TAA', 'TAA')],
        name="Anti Aliasing", description="Post-process anti aliasing technique", default='SMAA', update=update_renderpath)
    rp_volumetriclight: BoolProperty(name="Volumetric Light", description="Use volumetric lighting", default=False, update=update_renderpath)
    rp_ssr: BoolProperty(name="SSR", description="Screen space reflections", default=False, update=update_renderpath)
    rp_ss_refraction: BoolProperty(name="SSRefraction", description="Screen space refractions", default=False, update=update_renderpath)
    rp_ssgi: EnumProperty(
        items=[('Off', 'No AO', 'Off'),
                ('SSAO', 'SSAO', 'Screen space ambient occlusion'),
                ('RTAO', 'RTAO', 'Ray-traced ambient occlusion'),
                ('RTGI', 'RTGI', 'Ray-traced global illumination')
               ],
        name="SSGI", description="Screen space global illumination", default='SSAO', update=update_renderpath)
    rp_bloom: BoolProperty(name="Bloom", description="Bloom processing", default=False, update=update_renderpath)
    arm_bloom_follow_blender: BoolProperty(name="Use Blender Settings", description="Use Blender settings instead of Armory settings", default=True)
    rp_motionblur: EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Camera', 'Camera', 'Camera'),
               ('Object', 'Object', 'Object')],
        name="Motion Blur", description="Velocity buffer is used for object based motion blur", default='Off', update=update_renderpath)
    rp_translucency: BoolProperty(name="Translucency", description="Current render-path state", default=False)
    rp_translucency_state: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="Translucency", description="Order independent translucency", default='Auto', update=update_translucency_state)
    rp_decals: BoolProperty(name="Decals", description="Current render-path state", default=False)
    rp_decals_state: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="Decals", description="Decals pass", default='Auto', update=update_decals_state)
    rp_overlays: BoolProperty(name="Overlays", description="Current render-path state", default=False)
    rp_overlays_state: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="Overlays", description="X-Ray pass", default='Auto', update=update_overlays_state)
    rp_sss: BoolProperty(name="SSS", description="Current render-path state", default=False)
    rp_sss_state: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="SSS", description="Sub-surface scattering pass", default='Auto', update=update_sss_state)
    rp_blending: BoolProperty(name="Blending", description="Current render-path state", default=False)
    rp_blending_state: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="Blending", description="Blending pass", default='Auto', update=update_blending_state)
    rp_draw_order: EnumProperty(
        items=[('Auto', 'Auto', 'Auto'),
               ('Distance', 'Distance', 'Distance'),
               ('Shader', 'Shader', 'Shader')],
        name='Draw Order', description='Sort objects', default='Auto', update=assets.invalidate_compiled_data)
    rp_depth_texture: BoolProperty(name="Depth Texture", description="Current render-path state", default=False)
    rp_depth_texture_state: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name='Depth Texture', description='Whether materials can read from a depth texture', default='Auto', update=update_depth_texture_state)
    rp_stereo: BoolProperty(name="VR", description="Stereo rendering", default=False, update=update_renderpath)
    rp_water: BoolProperty(name="Water", description="Enable water surface pass", default=False, update=update_renderpath)
    rp_pp: BoolProperty(name="Realtime postprocess", description="Realtime postprocess", default=False, update=update_renderpath)
    rp_voxels: BoolProperty(name="Voxel AO", description="Ambient occlusion", default=False, update=update_renderpath)
    rp_voxelgi_resolution: EnumProperty(
        items=[('32', '32', '32'),
               ('64', '64', '64'),
               ('128', '128', '128'),
               ('256', '256', '256'),
               ('512', '512', '512')],
        name="Resolution", description="3D texture resolution", default='128', update=update_renderpath)
    rp_voxelgi_resolution_z: EnumProperty(
        items=[('2.0', '2.0', '2.0'),
               ('1.0', '1.0', '1.0'),
               ('0.5', '0.5', '0.5'),
               ('0.25', '0.25', '0.25')],
        name="Resolution Z", description="3D texture z resolution multiplier", default='1.0', update=update_renderpath)
    arm_clouds: BoolProperty(name="Clouds", description="Enable clouds pass", default=False, update=assets.invalidate_shader_cache)
    arm_ssrs: BoolProperty(name="SSRS", description="Screen-space ray-traced shadows", default=False, update=assets.invalidate_shader_cache)
    arm_micro_shadowing: BoolProperty(name="Micro Shadowing", description="Micro shadowing based on ambient occlusion", default=False, update=assets.invalidate_shader_cache)
    arm_texture_filter: EnumProperty(
        items=[('Anisotropic', 'Anisotropic', 'Anisotropic'),
               ('Linear', 'Linear', 'Linear'),
               ('Point', 'Closest', 'Point'),
               ('Manual', 'Manual', 'Manual')],
        name="Texture Filtering", description="Set Manual to honor interpolation setting on Image Texture node", default='Anisotropic')
    arm_material_model: EnumProperty(
        items=[('Full', 'Full', 'Full'),
               ('Mobile', 'Mobile', 'Mobile'),
               ('Solid', 'Solid', 'Solid'),
               ],
        name="Materials", description="Material builder", default='Full', update=update_material_model)
    arm_rp_displacement: EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Vertex', 'Vertex', 'Vertex'),
               ('Tessellation', 'Tessellation', 'Tessellation')],
        name="Displacement", description="Enable material displacement", default='Vertex', update=assets.invalidate_shader_cache)
    arm_tess_mesh_inner: IntProperty(name="Inner", description="Inner tessellation level", default=7)
    arm_tess_mesh_outer: IntProperty(name="Outer", description="Outer tessellation level", default=7)
    arm_tess_shadows_inner: IntProperty(name="Inner", description="Inner tessellation level", default=7)
    arm_tess_shadows_outer: IntProperty(name="Outer", description="Outer tessellation level", default=7)
    arm_rp_resolution: EnumProperty(
        items=[('Display', 'Display', 'Display'),
               ('Custom', 'Custom', 'Custom')],
        name="Resolution", description="Resolution to perform rendering at", default='Display', update=update_renderpath)
    arm_rp_resolution_size: IntProperty(name="Size", description="Resolution height in pixels(for example 720p), width is auto-fit to preserve aspect ratio", default=720, min=0, update=update_renderpath)
    arm_rp_resolution_filter: EnumProperty(
        items=[('Linear', 'Linear', 'Linear'),
               ('Point', 'Closest', 'Point')],
        name="Filter", description="Scaling filter", default='Linear')
    rp_dynres: BoolProperty(name="Dynamic Resolution", description="Dynamic resolution scaling for performance", default=False, update=update_renderpath)
    rp_chromatic_aberration: BoolProperty(name="Chromatic Aberration", description="Add chromatic aberration (scene fringe)", default=False, update=assets.invalidate_shader_cache)
    arm_ssr_half_res: BoolProperty(name="Half Res", description="Trace in half resolution", default=False, update=update_renderpath)
    arm_voxelgi_dimensions: FloatProperty(name="Dimensions", description="Voxelization bounds",default=16, update=assets.invalidate_compiled_data)
    arm_voxelgi_revoxelize: BoolProperty(name="Revoxelize", description="Revoxelize scene each frame", default=False, update=assets.invalidate_shader_cache)
    arm_voxelgi_temporal: BoolProperty(name="Temporal Filter", description="Use temporal filtering to stabilize voxels", default=False, update=assets.invalidate_shader_cache)
    arm_voxelgi_camera: BoolProperty(name="Dynamic Camera", description="Use camera as voxelization origin", default=False, update=assets.invalidate_shader_cache)
    arm_voxelgi_shadows: BoolProperty(name="Shadows", description="Use voxels to render shadows", default=False, update=update_renderpath)
    arm_samples_per_pixel: EnumProperty(
        items=[('1', '1', '1'),
               ('2', '2', '2'),
               ('4', '4', '4'),
               ('8', '8', '8'),
               ('16', '16', '16')],
        name="MSAA", description="Samples per pixel usable for render paths drawing directly to framebuffer", default='1')

    arm_voxelgi_cones: EnumProperty(
        items=[('9', '9', '9'),
               ('5', '5', '5'),
               ('3', '3', '3'),
               ('1', '1', '1'),
               ],
        name="Cones", description="Number of cones to trace", default='5', update=assets.invalidate_shader_cache)
    arm_voxelgi_occ: FloatProperty(name="Occlusion", description="", default=1.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_env: FloatProperty(name="Env Map", description="Contribute light from environment map", default=0.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_step: FloatProperty(name="Step", description="Step size", default=1.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_offset: FloatProperty(name="Offset", description="Ray offset", default=1.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_range: FloatProperty(name="Range", description="Maximum range", default=2.0, update=assets.invalidate_shader_cache)
    arm_voxelgi_aperture: FloatProperty(name="Aperture", description="Cone aperture for shadow trace", default=1.0, update=assets.invalidate_shader_cache)
    arm_sss_width: FloatProperty(name="Width", description="SSS blur strength", default=1.0, update=assets.invalidate_shader_cache)
    arm_water_color: FloatVectorProperty(name="Color", size=3, default=[1, 1, 1], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    arm_water_level: FloatProperty(name="Level", default=0.0, update=assets.invalidate_shader_cache)
    arm_water_displace: FloatProperty(name="Displace", default=1.0, update=assets.invalidate_shader_cache)
    arm_water_speed: FloatProperty(name="Speed", default=1.0, update=assets.invalidate_shader_cache)
    arm_water_freq: FloatProperty(name="Freq", default=1.0, update=assets.invalidate_shader_cache)
    arm_water_density: FloatProperty(name="Density", default=1.0, update=assets.invalidate_shader_cache)
    arm_water_refract: FloatProperty(name="Refract", default=1.0, update=assets.invalidate_shader_cache)
    arm_water_reflect: FloatProperty(name="Reflect", default=1.0, update=assets.invalidate_shader_cache)
    arm_ssgi_strength: FloatProperty(name="Strength", default=1.0, update=assets.invalidate_shader_cache)
    arm_ssgi_radius: FloatProperty(name="Radius", default=1.0, update=assets.invalidate_shader_cache)
    arm_ssgi_step: FloatProperty(name="Step", default=2.0, update=assets.invalidate_shader_cache)
    arm_ssgi_max_steps: IntProperty(name="Max Steps", default=8, update=assets.invalidate_shader_cache)
    arm_ssgi_rays: EnumProperty(
        items=[('9', '9', '9'),
               ('5', '5', '5'),
               ],
        name="Rays", description="Number of rays to trace for RTAO", default='5', update=assets.invalidate_shader_cache)
    arm_ssgi_half_res: BoolProperty(name="Half Res", description="Trace in half resolution", default=False, update=assets.invalidate_shader_cache)
    arm_bloom_threshold: FloatProperty(name="Threshold", description="Brightness above which a pixel is contributing to the bloom effect", min=0, default=0.8, update=assets.invalidate_shader_cache)
    arm_bloom_knee: FloatProperty(name="Knee", description="Smoothen transition around the threshold (higher values = smoother transition)", min=0, max=1, default=0.5, update=assets.invalidate_shader_cache)
    arm_bloom_strength: FloatProperty(name="Strength", description="Strength of the bloom effect", min=0, default=0.05, update=assets.invalidate_shader_cache)
    arm_bloom_radius: FloatProperty(name="Radius", description="Glow radius (screen-size independent)", min=0, default=6.5, update=assets.invalidate_shader_cache)
    arm_bloom_anti_flicker: BoolProperty(name="Anti-Flicker Filter", description="Apply a filter to reduce flickering caused by fireflies (single very bright pixels)", default=True, update=assets.invalidate_shader_cache)
    arm_bloom_quality: EnumProperty(
        name="Quality",
        description="Resampling quality of the bloom pass",
        items=[
            ("low", "Low", "Lowest visual quality but best performance"),
            ("medium", "Medium", "Compromise between quality and performance"),
            ("high", "High", "Best quality, but slowest")
        ],
        default="medium",
        update=assets.invalidate_shader_cache
    )
    arm_motion_blur_intensity: FloatProperty(name="Intensity", default=1.0, update=assets.invalidate_shader_cache)
    arm_ssr_ray_step: FloatProperty(name="Step", default=0.04, update=assets.invalidate_shader_cache)
    arm_ssr_min_ray_step: FloatProperty(name="Step Min", default=0.05, update=assets.invalidate_shader_cache)
    arm_ssr_search_dist: FloatProperty(name="Search", default=5.0, update=assets.invalidate_shader_cache)
    arm_ssr_falloff_exp: FloatProperty(name="Falloff", default=5.0, update=assets.invalidate_shader_cache)
    arm_ssr_jitter: FloatProperty(name="Jitter", default=0.6, update=assets.invalidate_shader_cache)
    arm_ss_refraction_ray_step: FloatProperty(name="Step", default=0.04, update=assets.invalidate_shader_cache)
    arm_ss_refraction_min_ray_step: FloatProperty(name="Step Min", default=0.05, update=assets.invalidate_shader_cache)
    arm_ss_refraction_search_dist: FloatProperty(name="Search", default=5.0, update=assets.invalidate_shader_cache)
    arm_ss_refraction_falloff_exp: FloatProperty(name="Falloff", default=5.0, update=assets.invalidate_shader_cache)
    arm_ss_refraction_jitter: FloatProperty(name="Jitter", default=0.6, update=assets.invalidate_shader_cache)
    arm_volumetric_light_air_turbidity: FloatProperty(name="Air Turbidity", default=1.0, update=assets.invalidate_shader_cache)
    arm_volumetric_light_air_color: FloatVectorProperty(name="Air Color", size=3, default=[1.0, 1.0, 1.0], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    arm_volumetric_light_steps: IntProperty(name="Steps", default=20, min=0, update=assets.invalidate_shader_cache)
    arm_shadowmap_split: FloatProperty(name="Cascade Split", description="Split factor for cascaded shadow maps, higher factor favors detail on close surfaces", default=0.8, update=assets.invalidate_shader_cache)
    arm_shadowmap_bounds: FloatProperty(name="Cascade Bounds", description="Multiply cascade bounds to capture bigger area", default=1.0, update=assets.invalidate_compiled_data)
    arm_autoexposure_strength: FloatProperty(name="Auto Exposure Strength", default=1.0, update=assets.invalidate_shader_cache)
    arm_autoexposure_speed: FloatProperty(name="Auto Exposure Speed", default=1.0, update=assets.invalidate_shader_cache)
    arm_ssrs_ray_step: FloatProperty(name="Step", default=0.01, update=assets.invalidate_shader_cache)
    arm_chromatic_aberration_type: EnumProperty(
        items=[('Simple', 'Simple', 'Simple'),
               ('Spectral', 'Spectral', 'Spectral'),
               ],
        name="Aberration type", description="Aberration type", default='Simple', update=assets.invalidate_shader_cache)
    arm_chromatic_aberration_strength: FloatProperty(name="Strength", default=2.00, update=assets.invalidate_shader_cache)
    arm_chromatic_aberration_samples: IntProperty(name="Samples", default=32, min=8, update=assets.invalidate_shader_cache)
    # Compositor
    arm_letterbox: BoolProperty(name="Letterbox", default=False, update=assets.invalidate_shader_cache)
    arm_letterbox_color: FloatVectorProperty(name="Color", size=3, default=[0, 0, 0], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    arm_letterbox_size: FloatProperty(name="Size", default=0.1, update=assets.invalidate_shader_cache)
    arm_distort: BoolProperty(name="Distort", default=False, update=assets.invalidate_shader_cache)
    arm_distort_strength: FloatProperty(name="Strength", default=2.0, update=assets.invalidate_shader_cache)
    arm_grain: BoolProperty(name="Film Grain", default=False, update=assets.invalidate_shader_cache)
    arm_grain_strength: FloatProperty(name="Strength", default=2.0, update=assets.invalidate_shader_cache)
    arm_sharpen: BoolProperty(name="Sharpen", default=False, update=assets.invalidate_shader_cache)
    arm_sharpen_strength: FloatProperty(name="Strength", default=0.25, update=assets.invalidate_shader_cache)
    arm_fog: BoolProperty(name="Volumetric Fog", default=False, update=assets.invalidate_shader_cache)
    arm_fog_color: FloatVectorProperty(name="Color", size=3, subtype='COLOR', default=[0.5, 0.6, 0.7], min=0, max=1, update=assets.invalidate_shader_cache)
    arm_fog_amounta: FloatProperty(name="Amount A", default=0.25, update=assets.invalidate_shader_cache)
    arm_fog_amountb: FloatProperty(name="Amount B", default=0.5, update=assets.invalidate_shader_cache)
    arm_tonemap: EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Filmic', 'Filmic', 'Filmic'),
               ('Filmic2', 'Filmic2', 'Filmic2'),
               ('Reinhard', 'Reinhard', 'Reinhard'),
               ('Uncharted', 'Uncharted', 'Uncharted')],
        name='Tonemap', description='Tonemapping operator', default='Filmic', update=assets.invalidate_shader_cache)
    arm_fisheye: BoolProperty(name="Fish Eye", default=False, update=assets.invalidate_shader_cache)
    arm_vignette: BoolProperty(name="Vignette", default=False, update=assets.invalidate_shader_cache)
    arm_vignette_strength: FloatProperty(name="Strength", default=0.7, update=assets.invalidate_shader_cache)
    arm_lensflare: BoolProperty(name="Lens Flare", default=False, update=assets.invalidate_shader_cache)
    arm_lens: BoolProperty(name="Lens Texture", description="Grime Overlay", default=False, update=assets.invalidate_shader_cache)
    arm_lens_texture: StringProperty(name="Texture", description="Lens filepath", default="lenstexture.jpg", update=assets.invalidate_shader_cache)
    arm_lens_texture_masking: BoolProperty(name="Luminance Masking", description="Luminance masking", default=False, update=assets.invalidate_shader_cache)
    arm_lens_texture_masking_centerMinClip : FloatProperty(name="Center Min Clip", default=0.5, update=assets.invalidate_shader_cache)
    arm_lens_texture_masking_centerMaxClip : FloatProperty(name="Center Max Clip", default=0.1, update=assets.invalidate_shader_cache)
    arm_lens_texture_masking_luminanceMax : FloatProperty(name="Luminance Min", default=0.1, update=assets.invalidate_shader_cache)
    arm_lens_texture_masking_luminanceMin : FloatProperty(name="Luminance Max", default=2.5, update=assets.invalidate_shader_cache)
    arm_lens_texture_masking_brightnessExp : FloatProperty(name="Brightness Exponent", default=2.0, update=assets.invalidate_shader_cache)
    arm_lut: BoolProperty(name="LUT Colorgrading", description="Colorgrading", default=False, update=assets.invalidate_shader_cache)
    arm_lut_texture: StringProperty(name="Texture", description="LUT filepath", default="luttexture.jpg", update=assets.invalidate_shader_cache)
    arm_skin: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off')],
        name='Skinning', description='Enable skinning', default='On', update=assets.invalidate_shader_cache)
    arm_use_armature_deform_only: BoolProperty(name="Only Deform Bones", description="Only write deforming bones (and non-deforming ones when they have deforming children)", default=False, update=assets.invalidate_compiled_data)
    arm_skin_max_bones_auto: BoolProperty(name="Auto Bones", description="Calculate amount of maximum bones based on armatures", default=True, update=assets.invalidate_compiled_data)
    arm_skin_max_bones: IntProperty(name="Max Bones", default=50, min=1, max=3000, update=assets.invalidate_shader_cache)
    arm_morph_target: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off')],
        name='Shape key', description='Enable shape keys', default='On', update=assets.invalidate_shader_cache)
    arm_particles: EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off')],
        name='Particles', description='Enable particle simulation', default='On', update=assets.invalidate_shader_cache)
    # Material override flags
    arm_culling: BoolProperty(name="Culling", default=True)
    arm_two_sided_area_light: BoolProperty(name="Two-Sided Area Light", description="Emit light from both faces of area plane", default=False, update=assets.invalidate_shader_cache)

    @staticmethod
    def get_by_name(name: str) -> Optional['ArmRPListItem']:
        wrd = bpy.data.worlds['Arm']
        # Assume unique rp names
        for i in range(len(wrd.arm_rplist)):
            if wrd.arm_rplist[i].name == name:
                return wrd.arm_rplist[i]
        return None


class ARM_UL_RPList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ArmRPListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_rplist.new_item"
    bl_label = "New"

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self,context):
        layout = self.layout
        layout.prop(bpy.data.worlds['Arm'], 'rp_preset', expand=True)

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        wrd.arm_rplist.add()
        wrd.arm_rplist_index = len(wrd.arm_rplist) - 1
        wrd.arm_rplist[wrd.arm_rplist_index].name = bpy.data.worlds['Arm'].rp_preset
        update_preset(wrd, context)
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

class ArmRPListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_rplist.move_item"
    bl_label = "Move an item in the list"
    direction: EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    def move_index(self):
        # Move index of an item render queue while clamping it
        mdata = bpy.data.worlds['Arm']
        index = mdata.arm_rplist_index
        list_length = len(mdata.arm_rplist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        mdata.arm_rplist.move(index, new_index)
        mdata.arm_rplist_index = new_index

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        list = mdata.arm_rplist
        index = mdata.arm_rplist_index

        if self.direction == 'DOWN':
            neighbor = index + 1
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ArmRPListItem)
    bpy.utils.register_class(ARM_UL_RPList)
    bpy.utils.register_class(ArmRPListNewItem)
    bpy.utils.register_class(ArmRPListDeleteItem)
    bpy.utils.register_class(ArmRPListMoveItem)

    bpy.types.World.arm_rplist = CollectionProperty(type=ArmRPListItem)
    bpy.types.World.arm_rplist_index = IntProperty(name="Index for my_list", default=0, update=update_renderpath)

def unregister():
    bpy.utils.unregister_class(ArmRPListItem)
    bpy.utils.unregister_class(ARM_UL_RPList)
    bpy.utils.unregister_class(ArmRPListNewItem)
    bpy.utils.unregister_class(ArmRPListDeleteItem)
    bpy.utils.unregister_class(ArmRPListMoveItem)
