import os
import shutil
import arm.assets as assets
import arm.make_utils as make_utils
import arm.make_renderer as make_renderer
import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

def update_renderpath(self, context):
    if assets.invalidate_enabled == False:
        return
    make_renderer.set_renderpath(self, context)

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

def update_sss_state(self, context):
    if self.rp_sss_state == 'On':
        self.rp_sss = True
    elif self.rp_sss_state == 'Off':
        self.rp_sss = False
    else: # Auto - updates rp at build time if sss mat is used
        return
    update_renderpath(self, context)

class ArmRPListItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Path")

    rp_renderer = EnumProperty(
        items=[('Forward', 'Forward', 'Forward'),
               ('Deferred', 'Deferred', 'Deferred'),
               ('Deferred Plus', 'Deferred Plus', 'Deferred Plus'),
               ],
        name="Renderer", description="Renderer type", default='Deferred', update=update_renderpath)
    rp_depthprepass = bpy.props.BoolProperty(name="Depth Prepass", description="Depth Prepass for mesh context", default=False, update=update_renderpath)
    rp_hdr = bpy.props.BoolProperty(name="HDR", description="Render in HDR Space", default=True, update=update_renderpath)
    rp_render_to_texture = bpy.props.BoolProperty(name="Post Process", description="Render scene to texture for further processing", default=True, update=update_renderpath)
    rp_background = EnumProperty(
      items=[('World', 'World', 'World'),
             ('Clear', 'Clear', 'Clear'),
             ('None', 'None', 'None'),
      ],
      name="Background", description="Background type", default='World', update=update_renderpath)    
    rp_compositornodes = bpy.props.BoolProperty(name="Compositor", description="Draw compositor nodes", default=True, update=update_renderpath)
    rp_shadowmap = EnumProperty(
        items=[('None', 'None', 'None'),
               ('512', '512', '512'),
               ('1024', '1024', '1024'),
               ('2048', '2048', '2048'),
               ('4096', '4096', '4096'),
               ('8192', '8192', '8192'),
               ('16384', '16384', '16384'),],
        name="Shadow Map", description="Shadow map resolution", default='2048', update=update_renderpath)
    rp_shadowmap_cascades = EnumProperty(
        items=[('1', '1', '1'),
               ('2', '2', '2'),
               ('3', '3', '3'),
               ('4', '4', '4')],
        name="Cascades", description="Shadow map cascades", default='3', update=update_renderpath)
    rp_supersampling = EnumProperty(
        items=[('1', '1X', '1X'),
               ('2', '2X', '2X'),
               ('4', '4X', '4X')],
        name="Super Sampling", description="Screen resolution multiplier", default='1', update=update_renderpath)
    rp_antialiasing = EnumProperty(
        items=[('None', 'None', 'None'),
               ('FXAA', 'FXAA', 'FXAA'),
               ('SMAA', 'SMAA', 'SMAA'),
               ('TAA', 'TAA', 'TAA')],
        name="Anti Aliasing", description="Post-process anti aliasing technique", default='SMAA', update=update_renderpath)
    rp_volumetriclight = bpy.props.BoolProperty(name="Volumetric Light", description="Use volumetric lighting", default=False, update=update_renderpath)
    rp_ssao = bpy.props.BoolProperty(name="SSAO", description="Screen space ambient occlusion", default=True, update=update_renderpath)
    rp_ssr = bpy.props.BoolProperty(name="SSR", description="Screen space reflections", default=False, update=update_renderpath)
    rp_dfao = bpy.props.BoolProperty(name="DFAO", description="Distance field ambient occlusion", default=False)
    rp_dfrs = bpy.props.BoolProperty(name="DFRS", description="Distance field ray-traced shadows", default=False)
    rp_dfgi = bpy.props.BoolProperty(name="DFGI", description="Distance field global illumination", default=False)
    rp_bloom = bpy.props.BoolProperty(name="Bloom", description="Bloom processing", default=False, update=update_renderpath)
    rp_eyeadapt = bpy.props.BoolProperty(name="Eye Adaptation", description="Auto-exposure based on histogram", default=False, update=update_renderpath)
    rp_rendercapture = bpy.props.BoolProperty(name="Render Capture", description="Save output as render result", default=False, update=update_renderpath)
    rp_motionblur = EnumProperty(
        items=[('None', 'None', 'None'),
               ('Camera', 'Camera', 'Camera'),
               ('Object', 'Object', 'Object')],
        name="Motion Blur", description="Velocity buffer is used for object based motion blur", default='None', update=update_renderpath)
    rp_translucency = bpy.props.BoolProperty(name="Translucency", description="Current render-path state", default=False)
    rp_translucency_state = bpy.props.EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Translucency", description="Order independent translucency", default='Auto', update=update_translucency_state)
    rp_decals = bpy.props.BoolProperty(name="Decals", description="Current render-path state", default=False)
    rp_decals_state = bpy.props.EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Decals", description="Decals pass", default='Auto', update=update_decals_state)
    rp_overlays = bpy.props.BoolProperty(name="Overlays", description="Current render-path state", default=False)
    rp_overlays_state = bpy.props.EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Overlays", description="X-Ray pass", default='Auto', update=update_overlays_state)
    rp_sss = bpy.props.BoolProperty(name="SSS", description="Current render-path state", default=False)
    rp_sss_state = bpy.props.EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'),
               ('Auto', 'Auto', 'Auto')],
        name="SSS", description="Sub-surface scattering pass", default='Auto', update=update_sss_state)
    rp_blending_state = bpy.props.EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off')],
        name="Blending", description="Additive blending pass", default='Off', update=update_renderpath)
    rp_stereo = bpy.props.BoolProperty(name="Stereo", description="Stereo rendering", default=False, update=update_renderpath)
    rp_greasepencil = bpy.props.BoolProperty(name="Grease Pencil", description="Render Grease Pencil data", default=False, update=update_renderpath)
    rp_ocean = bpy.props.BoolProperty(name="Ocean", description="Ocean pass", default=False, update=update_renderpath)
    
    rp_gi = bpy.props.EnumProperty(
        items=[('Off', 'Off', 'Off'),
               ('Voxel GI', 'Voxel GI', 'Voxel GI'),
               ('Voxel AO', 'Voxel AO', 'Voxel AO')
               ],
        name="Global Illumination", description="Dynamic global illumination", default='Off', update=update_renderpath)
    rp_voxelgi_resolution = bpy.props.EnumProperty(
        items=[('32', '32', '32'),
               ('64', '64', '64'),
               ('128', '128', '128'),
               ('256', '256', '256'),
               ('512', '512', '512')],
        name="Resolution", description="3D texture resolution", default='128', update=update_renderpath)
    rp_voxelgi_resolution_z = bpy.props.EnumProperty(
        items=[('1.0', '1.0', '1.0'),
               ('0.5', '0.5', '0.5'),
               ('0.25', '0.25', '0.25')],
        name="Resolution Z", description="3D texture z resolution multiplier", default='1.0', update=update_renderpath)
    arm_clouds = bpy.props.BoolProperty(name="Clouds", default=False, update=assets.invalidate_shader_cache)
    arm_pcss_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Soft Shadows", description="Percentage Closer Soft Shadows", default='Off', update=assets.invalidate_shader_cache)
    arm_ssrs = bpy.props.BoolProperty(name="SSRS", description="Screen-space ray-traced shadows", default=False, update=assets.invalidate_shader_cache)
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
    arm_tessellation = bpy.props.BoolProperty(name="Tessellation", description="Enable tessellation for height maps on supported targets", default=True, update=assets.invalidate_shader_cache)
    arm_rp_resolution = EnumProperty(
        items=[('Display', 'Display', 'Display'),
               ('480', '480p', '480p'), 
               ('720', '720p', '720p'), 
               ('1080', '1080p', '1080p'),
               ('1440', '1440p', '1440p'),
               ('2160', '2160p', '2160p')],
        name="Resolution", description="Render at specific resolution, regardless of display resolution", default='Display', update=update_renderpath)
    arm_ssr_half_res = bpy.props.BoolProperty(name="Half Res", description="Trace in half resolution", default=True, update=update_renderpath)

    rp_voxelgi_hdr = bpy.props.BoolProperty(name="HDR Voxels", description="Store voxels in RGBA64 instead of RGBA32", default=False, update=update_renderpath)
    arm_voxelgi_dimensions = bpy.props.FloatProperty(name="Dimensions", description="Voxelization bounds",default=16, update=assets.invalidate_shader_cache)
    arm_voxelgi_revoxelize = bpy.props.BoolProperty(name="Revoxelize", description="Revoxelize scene each frame", default=False, update=assets.invalidate_shader_cache)
    # arm_voxelgi_multibounce = bpy.props.BoolProperty(name="Multi-bounce", description="Accumulate multiple light bounces", default=False, update=assets.invalidate_shader_cache)
    arm_voxelgi_camera = bpy.props.BoolProperty(name="Dynamic Camera", description="Use camera as voxelization origin", default=False, update=assets.invalidate_shader_cache)
    # arm_voxelgi_anisotropic = bpy.props.BoolProperty(name="Anisotropic", description="Use anisotropic voxels", default=False, update=update_renderpath)
    arm_voxelgi_shadows = bpy.props.BoolProperty(name="Trace Shadows", description="Use voxels to render shadows", default=False, update=update_renderpath)
    arm_voxelgi_refraction = bpy.props.BoolProperty(name="Trace Refraction", description="Use voxels to render refraction", default=False, update=update_renderpath)
    arm_voxelgi_emission = bpy.props.BoolProperty(name="Emission Voxels", description="Encode emission into voxelized data", default=False, update=update_renderpath)
    arm_samples_per_pixel = EnumProperty(
        items=[('1', '1X', '1X'),
               ('2', '2X', '2X'),
               ('4', '4X', '4X'),
               ('8', '8X', '8X'),
               ('16', '16X', '16X')],
        name="MSAA", description="Samples per pixel usable for render paths drawing directly to framebuffer", default='1')  
    arm_ssao_half_res = bpy.props.BoolProperty(name="Half Res", description="Trace in half resolution", default=False, update=assets.invalidate_shader_cache)

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

    bpy.types.World.arm_rplist = bpy.props.CollectionProperty(type=ArmRPListItem)
    bpy.types.World.arm_rplist_index = bpy.props.IntProperty(name="Index for my_list", default=0, update=update_renderpath)

def unregister():
    bpy.utils.unregister_class(ArmRPListItem)
    bpy.utils.unregister_class(ArmRPList)
    bpy.utils.unregister_class(ArmRPListNewItem)
    bpy.utils.unregister_class(ArmRPListDeleteItem)
