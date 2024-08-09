import json
import os
import sys
import shutil
import textwrap
import mathutils

import bpy
from bpy.props import *

from arm.lightmapper.panels import scene

import arm.api
import arm.assets as assets
from arm.exporter import ArmoryExporter
import arm.log as log
import arm.logicnode.replacement
import arm.make as make
import arm.make_state as state
import arm.props as props
import arm.props_properties
import arm.props_traits
import arm.nodes_logic
import arm.ui_icons as ui_icons
import arm.utils
import arm.utils_vs
import arm.write_probes

if arm.is_reload(__name__):
    arm.api = arm.reload_module(arm.api)
    assets = arm.reload_module(assets)
    arm.exporter = arm.reload_module(arm.exporter)
    from arm.exporter import ArmoryExporter
    log = arm.reload_module(log)
    arm.logicnode.replacement = arm.reload_module(arm.logicnode.replacement)
    make = arm.reload_module(make)
    state = arm.reload_module(state)
    props = arm.reload_module(props)
    arm.props_properties = arm.reload_module(arm.props_properties)
    arm.props_traits = arm.reload_module(arm.props_traits)
    arm.nodes_logic = arm.reload_module(arm.nodes_logic)
    ui_icons = arm.reload_module(ui_icons)
    arm.utils = arm.reload_module(arm.utils)
    arm.utils_vs = arm.reload_module(arm.utils_vs)
    arm.write_probes = arm.reload_module(arm.write_probes)
else:
    arm.enable_reload(__name__)

class ARM_PT_ObjectPropsPanel(bpy.types.Panel):
    """Menu in object region."""
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        obj = bpy.context.object
        if obj == None:
            return

        col = layout.column()
        col.prop(obj, 'arm_export')
        if not obj.arm_export:
            return
        col.prop(obj, 'arm_spawn')
        col.prop(obj, 'arm_mobile')
        col.prop(obj, 'arm_animation_enabled')

        if obj.type == 'MESH':
            layout.prop(obj, 'arm_instanced')
            wrd = bpy.data.worlds['Arm']
            layout.prop_search(obj, "arm_tilesheet", wrd, "arm_tilesheetlist", text="Tilesheet")
            if obj.arm_tilesheet != '':
                selected_ts = None
                for ts in wrd.arm_tilesheetlist:
                    if ts.name == obj.arm_tilesheet:
                        selected_ts = ts
                        break
                layout.prop_search(obj, "arm_tilesheet_action", selected_ts, "arm_tilesheetactionlist", text="Action")
                layout.prop(obj, "arm_use_custom_tilesheet_node")

        # Properties list
        arm.props_properties.draw_properties(layout, obj)

        # Lightmapping props
        if obj.type == "MESH":
            row = layout.row(align=True)
            row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_use")

            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_use_default_channel")

                if not obj.TLM_ObjectProperties.tlm_use_default_channel:

                    row = layout.row()
                    row.prop_search(obj.TLM_ObjectProperties, "tlm_uv_channel", obj.data, "uv_layers", text='UV Channel')

                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_resolution")
                if obj.TLM_ObjectProperties.tlm_use_default_channel:
                    row = layout.row()
                    row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_unwrap_mode")
                row = layout.row()
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":

                    if scene.TLM_AtlasListItem >= 0 and len(scene.TLM_AtlasList) > 0:
                        row = layout.row()
                        item = scene.TLM_AtlasList[scene.TLM_AtlasListItem]
                        row.prop_search(obj.TLM_ObjectProperties, "tlm_atlas_pointer", scene, "TLM_AtlasList", text='Atlas Group')
                        row = layout.row()
                    else:
                        row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")
                        row = layout.row()

                else:
                    row = layout.row()
                    row.prop(obj.TLM_ObjectProperties, "tlm_postpack_object")
                    row = layout.row()


                if obj.TLM_ObjectProperties.tlm_postpack_object and obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode != "AtlasGroupA":
                    if scene.TLM_PostAtlasListItem >= 0 and len(scene.TLM_PostAtlasList) > 0:
                        row = layout.row()
                        item = scene.TLM_PostAtlasList[scene.TLM_PostAtlasListItem]
                        row.prop_search(obj.TLM_ObjectProperties, "tlm_postatlas_pointer", scene, "TLM_PostAtlasList", text='Atlas Group')
                        row = layout.row()

                    else:
                        row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")
                        row = layout.row()

                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_unwrap_margin")
                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filter_override")
                row = layout.row()
                if obj.TLM_ObjectProperties.tlm_mesh_filter_override:
                    row = layout.row(align=True)
                    row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_mode")
                    row = layout.row(align=True)
                    if obj.TLM_ObjectProperties.tlm_mesh_filtering_mode == "Gaussian":
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_gaussian_strength")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")
                    elif obj.TLM_ObjectProperties.tlm_mesh_filtering_mode == "Box":
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_box_strength")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")
                    elif obj.TLM_ObjectProperties.tlm_mesh_filtering_mode == "Bilateral":
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_bilateral_diameter")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_bilateral_color_deviation")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_bilateral_coordinate_deviation")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")
                    else:
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_median_kernel", expand=True)
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")

                #If UV Packer installed
                if "UV-Packer" in bpy.context.preferences.addons.keys():
                    row.prop(obj.TLM_ObjectProperties, "tlm_use_uv_packer")
                    if obj.TLM_ObjectProperties.tlm_use_uv_packer:
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_uv_packer_padding")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_uv_packer_packing_engine")

class ARM_PT_ModifiersPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        obj = bpy.context.object
        if obj == None:
            return
        layout.operator("arm.invalidate_cache")

class ARM_PT_ParticlesPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "particle"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        obj = bpy.context.particle_system
        if obj == None:
            return

        layout.prop(obj.settings, 'arm_loop')
        layout.prop(obj.settings, 'arm_count_mult')

class ARM_PT_PhysicsPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        obj = bpy.context.object
        if obj == None:
            return

        rb = obj.rigid_body
        if rb is not None:
            col = layout.column()
            row = col.row()
            row.alignment = 'RIGHT'

            rb_type = 'Dynamic'
            if ArmoryExporter.rigid_body_static(rb):
                rb_type = 'Static'
            if rb.kinematic:
                rb_type = 'Kinematic'
            row.label(text=(f'Rigid Body Export Type: {rb_type}'), icon='AUTO')

            layout.prop(obj, 'arm_rb_linear_factor')
            layout.prop(obj, 'arm_rb_angular_factor')
            layout.prop(obj, 'arm_rb_angular_friction')
            layout.prop(obj, 'arm_rb_trigger')
            layout.prop(obj, 'arm_rb_ccd')

        if obj.soft_body is not None:
            layout.prop(obj, 'arm_soft_body_margin')

        if obj.rigid_body_constraint is not None:
            layout.prop(obj, 'arm_relative_physics_constraint')

class ARM_OT_AddArmatureRootMotion(bpy.types.Operator):
    bl_idname = "arm.add_root_motion_bone"
    bl_label = "Add root bone"
    bl_description = "Add a new bone and set it as the root bone. This may be used for root motion."

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj.mode == 'EDIT':
            return False
        armature = obj.data
        if armature.bones:
            if armature.bones.active:
                return True

    def execute(self, context):
        obj = context.object
        current_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        armature = obj.data
        edit_bones = armature.edit_bones
        current_root_pos = edit_bones.active.head
        current_root_len = edit_bones.active.length
        new_root = edit_bones.new("ArmoryRoot")
        new_root.head = current_root_pos
        new_root.tail = new_root.head + mathutils.Vector((0.0, 0.0, current_root_len))
        bpy.ops.object.mode_set(mode=current_mode)
        return{'FINISHED'}

# Menu in data region
class ARM_PT_DataPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        obj = bpy.context.object
        if obj == None:
            return

        wrd = bpy.data.worlds['Arm']
        if obj.type == 'CAMERA':
            layout.prop(obj.data, 'arm_frustum_culling')
        elif obj.type == 'MESH' or obj.type == 'FONT' or obj.type == 'META':
            layout.prop(obj.data, 'arm_dynamic_usage')
            layout.operator("arm.invalidate_cache")
        elif obj.type == 'LIGHT':
            layout.prop(obj.data, 'arm_clip_start')
            layout.prop(obj.data, 'arm_clip_end')
            layout.prop(obj.data, 'arm_fov')
            layout.prop(obj.data, 'arm_shadows_bias')
            layout.prop(wrd, 'arm_light_ies_texture')
            layout.prop(wrd, 'arm_light_clouds_texture')
        elif obj.type == 'SPEAKER':
            layout.prop(obj.data, 'arm_play_on_start')
            layout.prop(obj.data, 'arm_loop')
            layout.prop(obj.data, 'arm_stream')
        elif obj.type == 'ARMATURE':
            layout.prop(obj.data, 'arm_autobake')
            layout.prop(obj.data, 'arm_relative_bone_constraints')
            if obj.data.bones:
                if obj.data.bones.active:
                    layout.label(text='Current Root: ' + obj.data.bones.active.name)
            layout.operator('arm.add_root_motion_bone', text='Add new root bone', icon='ADD')
            pass

class ARM_PT_WorldPropsPanel(bpy.types.Panel):
    bl_label = "Armory World Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        world = context.world
        if world is None:
            return

        layout.prop(world, 'arm_use_clouds')
        col = layout.column(align=True)
        col.enabled = world.arm_use_clouds
        col.prop(world, 'arm_darken_clouds')
        col.prop(world, 'arm_clouds_lower')
        col.prop(world, 'arm_clouds_upper')
        col.prop(world, 'arm_clouds_precipitation')
        col.prop(world, 'arm_clouds_secondary')
        col.prop(world, 'arm_clouds_wind')
        col.prop(world, 'arm_clouds_steps')

class ARM_PT_ScenePropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = bpy.context.scene
        if scene == None:
            return
        row = layout.row()
        column = row.column()
        row.prop(scene, 'arm_export')

class InvalidateCacheButton(bpy.types.Operator):
    """Delete cached mesh data"""
    bl_idname = "arm.invalidate_cache"
    bl_label = "Invalidate Cache"

    def execute(self, context):
        context.object.data.arm_cached = False
        return{'FINISHED'}

class InvalidateMaterialCacheButton(bpy.types.Operator):
    """Delete cached material data"""
    bl_idname = "arm.invalidate_material_cache"
    bl_label = "Invalidate Cache"

    def execute(self, context):
        context.material.arm_cached = False
        context.material.signature = ''
        return{'FINISHED'}

class ARM_OT_NewCustomMaterial(bpy.types.Operator):
    bl_idname = "arm.new_custom_material"
    bl_label = "New Custom Material"
    bl_description = "Add a new custom material. This will create all the necessary files and folders"

    def poll_mat_name(self, context):
        project_dir = arm.utils.get_fp()
        shader_dir_dst = os.path.join(project_dir, 'Shaders')
        mat_name = arm.utils.safestr(self.mat_name)

        self.mat_exists = os.path.isdir(os.path.join(project_dir, 'Bundled', mat_name))

        vert_exists = os.path.isfile(os.path.join(shader_dir_dst, f'{mat_name}.vert.glsl'))
        frag_exists = os.path.isfile(os.path.join(shader_dir_dst, f'{mat_name}.frag.glsl'))
        self.shader_exists = vert_exists or frag_exists

    mat_name: StringProperty(
        name='Material Name', description='The name of the new material',
        default='MyCustomMaterial',
        update=poll_mat_name)
    mode: EnumProperty(
        name='Target RP', description='Choose for which render path mode the new material is created',
        default='deferred',
        items=[('deferred', 'Deferred', 'Create the material for a deferred render path'),
               ('forward', 'Forward', 'Create the material for a forward render path')])
    mat_exists: BoolProperty(
        name='Material Already Exists',
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'})
    shader_exists: BoolProperty(
        name='Shaders Already Exist',
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'})

    def invoke(self, context, event):
        if not bpy.data.is_saved:
            self.report({'INFO'}, "Please save your file first")
            return {"CANCELLED"}

        # Try to set deferred/forward based on the selected render path
        try:
            self.mode = 'forward' if arm.utils.get_rp().rp_renderer == 'Forward' else 'deferred'
        except IndexError:
            # No render path, use default (deferred)
            pass

        self.poll_mat_name(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, 'mat_name')
        layout.prop(self, 'mode', expand=True)

        if self.mat_exists:
            box = layout.box()
            box.alert = True
            col = box.column(align=True)
            col.label(text='A custom material with that name already exists,', icon='ERROR')
            col.label(text='clicking on \'OK\' will override the material!', icon='BLANK1')

        if self.shader_exists:
            box = layout.box()
            box.alert = True
            col = box.column(align=True)
            col.label(text='Shader file(s) with that name already exists,', icon='ERROR')
            col.label(text='clicking on \'OK\' will override the shader(s)!', icon='BLANK1')

    def execute(self, context):
        if self.mat_name == '':
            return {'CANCELLED'}

        project_dir = arm.utils.get_fp()
        shader_dir_src = os.path.join(arm.utils.get_sdk_path(), 'armory', 'Shaders', 'custom_mat_presets')
        shader_dir_dst = os.path.join(project_dir, 'Shaders')
        mat_name = arm.utils.safestr(self.mat_name)
        mat_dir = os.path.join(project_dir, 'Bundled', mat_name)

        os.makedirs(mat_dir, exist_ok=True)
        os.makedirs(shader_dir_dst, exist_ok=True)

        # Shader data
        if self.mode == 'forward':
            col_attachments = ['RGBA64']
            constants = [{'link': '_worldViewProjectionMatrix', 'name': 'WVP', 'type': 'mat4'}]
            vertex_elems = [{'name': 'pos', 'data': 'short4norm'}]
        else:
            col_attachments = ['RGBA64', 'RGBA64']
            constants = [
                {'link': '_worldViewProjectionMatrix', 'name': 'WVP', 'type': 'mat4'},
                {'link': '_normalMatrix', 'name': 'N', 'type': 'mat3'}
            ]
            vertex_elems = [
                {'name': 'pos', 'data': 'short4norm'},
                {'name': 'nor', 'data': 'short2norm'}
            ]

        con = {
            'color_attachments':  col_attachments,
            'compare_mode': 'less',
            'constants': constants,
            'cull_mode': 'clockwise',
            'depth_write': True,
            'fragment_shader': f'{mat_name}.frag',
            'name': 'mesh',
            'texture_units': [],
            'vertex_shader': f'{mat_name}.vert',
            'vertex_elements': vertex_elems
        }
        data = {
            'shader_datas': [{
                'contexts': [con],
                'name': f'{mat_name}'
            }]
        }

        # Save shader data file
        with open(os.path.join(mat_dir, f'{mat_name}.json'), 'w') as datafile:
            json.dump(data, datafile, indent=4, sort_keys=True)

        # Copy preset shaders to project
        if self.mode == 'forward':
            shutil.copy(os.path.join(shader_dir_src, 'custom_mat_forward.frag.glsl'), os.path.join(shader_dir_dst, f'{mat_name}.frag.glsl'))
            shutil.copy(os.path.join(shader_dir_src, 'custom_mat_forward.vert.glsl'), os.path.join(shader_dir_dst, f'{mat_name}.vert.glsl'))
        else:
            shutil.copy(os.path.join(shader_dir_src, 'custom_mat_deferred.frag.glsl'), os.path.join(shader_dir_dst, f'{mat_name}.frag.glsl'))
            shutil.copy(os.path.join(shader_dir_src, 'custom_mat_deferred.vert.glsl'), os.path.join(shader_dir_dst, f'{mat_name}.vert.glsl'))

        # True if called from the material properties tab, else it was called from the search menu
        if hasattr(context, 'material') and context.material is not None:
            context.material.arm_custom_material = mat_name

        return{'FINISHED'}

class ARM_PG_BindTexturesListItem(bpy.types.PropertyGroup):
    uniform_name: StringProperty(
        name='Uniform Name',
        description='The name of the sampler uniform as used in the shader',
        default='ImageTexture',
    )

    image: PointerProperty(
        name='Image',
        type=bpy.types.Image,
        description='The image to attach to the texture unit',
    )

class ARM_UL_BindTexturesList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item: ARM_PG_BindTexturesListItem, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        if item.image is not None:
            row.label(text=item.uniform_name, icon_value=item.image.preview.icon_id)
        else:
            row.label(text='<empty>', icon='ERROR')

class ARM_OT_BindTexturesListNewItem(bpy.types.Operator):
    bl_idname = "arm_bind_textures_list.new_item"
    bl_label = "Add Texture Binding"
    bl_description = "Add a new texture binding to the list"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        mat = context.material
        if mat is None:
            return False
        return True

    def execute(self, context):
        mat = context.material
        mat.arm_bind_textures_list.add()
        mat.arm_bind_textures_list_index = len(mat.arm_bind_textures_list) - 1
        return{'FINISHED'}

class ARM_OT_BindTexturesListDeleteItem(bpy.types.Operator):
    bl_idname = "arm_bind_textures_list.delete_item"
    bl_label = "Remove Texture Binding"
    bl_description = "Delete the selected texture binding from the list"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        mat = context.material
        if mat is None:
            return False
        return len(mat.arm_bind_textures_list) > 0

    def execute(self, context):
        mat = context.material
        lst = mat.arm_bind_textures_list
        index = mat.arm_bind_textures_list_index

        if len(lst) <= index:
            return{'FINISHED'}

        lst.remove(index)

        if index > 0:
            index = index - 1
        mat.arm_bind_textures_list_index = index

        return{'FINISHED'}

class ARM_PT_MaterialPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        mat = bpy.context.material
        if mat is None:
            return

        layout.prop(mat, 'arm_cast_shadow')
        columnb = layout.column()
        wrd = bpy.data.worlds['Arm']
        columnb.enabled = len(wrd.arm_rplist) > 0 and arm.utils.get_rp().rp_renderer == 'Forward'
        columnb.prop(mat, 'arm_receive_shadow')
        layout.prop(mat, 'arm_ignore_irradiance')
        layout.prop(mat, 'arm_two_sided')
        columnb = layout.column()
        columnb.enabled = not mat.arm_two_sided
        columnb.prop(mat, 'arm_cull_mode')
        layout.prop(mat, 'arm_material_id')
        layout.prop(mat, 'arm_depth_read')
        layout.prop(mat, 'arm_overlay')
        layout.prop(mat, 'arm_decal')
        layout.prop(mat, 'arm_discard')
        columnb = layout.column()
        columnb.enabled = mat.arm_discard
        columnb.prop(mat, 'arm_discard_opacity')
        columnb.prop(mat, 'arm_discard_opacity_shadows')
        row = layout.row(align=True)
        row.prop(mat, 'arm_custom_material')
        row.operator('arm.new_custom_material', text='', icon='ADD')
        layout.prop(mat, 'arm_skip_context')
        layout.prop(mat, 'arm_particle_fade')
        layout.prop(mat, 'arm_billboard')

        layout.operator("arm.invalidate_material_cache")

class ARM_PT_BindTexturesPropsPanel(bpy.types.Panel):
    bl_label = "Bind Textures"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_MaterialPropsPanel"

    @classmethod
    def poll(cls, context):
        mat = context.material
        if mat is None:
            return False

        return mat.arm_custom_material != ''

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        mat = bpy.context.material
        if mat is None:
            return

        row = layout.row(align=True)
        col = row.column(align=True)
        col.template_list('ARM_UL_BindTexturesList', '', mat, 'arm_bind_textures_list', mat, 'arm_bind_textures_list_index')

        if mat.arm_bind_textures_list_index >= 0 and len(mat.arm_bind_textures_list) > 0:
            item = mat.arm_bind_textures_list[mat.arm_bind_textures_list_index]
            box = col.box()

            if item.image is None:
                _row = box.row()
                _row.alert = True
                _row.alignment = 'RIGHT'
                _row.label(text="No image selected, skipping export")

            box.prop(item, 'uniform_name')
            box.prop(item, 'image')

        col = row.column(align=True)
        col.operator("arm_bind_textures_list.new_item", icon='ADD', text="")
        col.operator("arm_bind_textures_list.delete_item", icon='REMOVE', text="")

class ARM_PT_MaterialDriverPropsPanel(bpy.types.Panel):
    """Per-material properties for custom render path drivers"""
    bl_label = "Armory Driver Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        mat = context.material
        if mat is None:
            return False

        wrd = bpy.data.worlds['Arm']
        if wrd.arm_rplist_index < 0 or len(wrd.arm_rplist) == 0:
            return False

        if len(arm.api.drivers) == 0:
            return False

        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
        return rpdat.rp_driver != 'Armory' and arm.api.drivers[rpdat.rp_driver]['draw_mat_props'] is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        wrd = bpy.data.worlds['Arm']
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
        arm.api.drivers[rpdat.rp_driver]['draw_mat_props'](layout, context.material)

class ARM_PT_MaterialBlendingPropsPanel(bpy.types.Panel):
    bl_label = "Blending"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_MaterialPropsPanel"

    def draw_header(self, context):
        if context.material is None:
            return
        self.layout.prop(context.material, 'arm_blending', text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        mat = bpy.context.material
        if mat is None:
            return

        flow = layout.grid_flow()
        flow.enabled = mat.arm_blending
        col = flow.column(align=True)
        col.prop(mat, 'arm_blending_source')
        col.prop(mat, 'arm_blending_destination')
        col.prop(mat, 'arm_blending_operation')
        flow.separator()

        col = flow.column(align=True)
        col.prop(mat, 'arm_blending_source_alpha')
        col.prop(mat, 'arm_blending_destination_alpha')
        col.prop(mat, 'arm_blending_operation_alpha')

class ARM_PT_ArmoryPlayerPanel(bpy.types.Panel):
    bl_label = "Armory Player"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.scale_y = 1.3
        if state.proc_play is None and state.proc_build is None:
            row.operator("arm.play", icon="PLAY")
        else:
            row.operator("arm.stop", icon="MESH_PLANE")
        row.operator("arm.clean_menu", icon="BRUSH_DATA")

        col = layout.box().column()
        col.prop(wrd, 'arm_runtime')
        col.prop(wrd, 'arm_play_camera')
        col.prop(wrd, 'arm_play_scene')
        col.prop_search(wrd, 'arm_play_renderpath', wrd, 'arm_rplist', text='Render Path')

        if log.num_warnings > 0:
            box = layout.box()
            box.alert = True

            col = box.column(align=True)
            warnings = 'warnings' if log.num_warnings > 1 else 'warning'
            col.label(text=f'{log.num_warnings} {warnings} occurred during compilation!', icon='ERROR')
            # Blank icon to achieve the same indentation as the line before
            # prevent showing "open console" twice:
            if log.num_errors == 0:
                col.label(text='Please open the console to get more information.', icon='BLANK1')

        if log.num_errors > 0:
            box = layout.box()
            box.alert = True
            # Less spacing between lines
            col = box.column(align=True)
            errors = 'errors' if log.num_errors > 1 else 'error'
            col.label(text=f'{log.num_errors} {errors} occurred during compilation!', icon='CANCEL')
            # Blank icon to achieve the same indentation as the line before
            col.label(text='Please open the console to get more information.', icon='BLANK1')

class ARM_PT_ArmoryExporterPanel(bpy.types.Panel):
    bl_label = "Armory Exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.scale_y = 1.3
        row.operator("arm.build_project", icon="MOD_BUILD")
        # row.operator("arm.patch_project")
        row.operator("arm.publish_project", icon="EXPORT")

        rows = 2
        if len(wrd.arm_exporterlist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ARM_UL_ExporterList", "The_List", wrd, "arm_exporterlist", wrd, "arm_exporterlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_exporterlist.new_item", icon='ADD', text="")
        col.operator("arm_exporterlist.delete_item", icon='REMOVE', text="")
        col.menu("ARM_MT_ExporterListSpecials", icon='DOWNARROW_HLT', text="")

        if len(wrd.arm_exporterlist) > 1:
            col.separator()
            op = col.operator("arm_exporterlist.move_item", icon='TRIA_UP', text="")
            op.direction = 'UP'
            op = col.operator("arm_exporterlist.move_item", icon='TRIA_DOWN', text="")
            op.direction = 'DOWN'

        if wrd.arm_exporterlist_index >= 0 and len(wrd.arm_exporterlist) > 0:
            item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
            box = layout.box().column()
            box.prop(item, 'arm_project_target')
            box.prop(item, 'arm_project_khamake')
            box.prop(item, arm.utils.target_to_gapi(item.arm_project_target))
            box.prop_search(item, "arm_project_rp", wrd, "arm_rplist", text="Render Path")
            box.prop_search(item, 'arm_project_scene', bpy.data, 'scenes', text='Scene')
            layout.separator()

        col = layout.column(align=True)
        col.prop(wrd, 'arm_project_name')
        col.prop(wrd, 'arm_project_package')
        col.prop(wrd, 'arm_project_bundle')

        col = layout.column(align=True)
        col.prop(wrd, 'arm_project_version')
        col.prop(wrd, 'arm_project_version_autoinc')

        col = layout.column()
        col.prop(wrd, 'arm_project_icon')

        col = layout.column(heading='Code Output', align=True)
        col.prop(wrd, 'arm_dce')
        col.prop(wrd, 'arm_compiler_inline')
        col.prop(wrd, 'arm_minify_js')
        col.prop(wrd, 'arm_no_traces')

        col = layout.column(heading='Data', align=True)
        col.prop(wrd, 'arm_minimize')
        col.prop(wrd, 'arm_optimize_data')
        col.prop(wrd, 'arm_asset_compression')
        col.prop(wrd, 'arm_single_data_file')

class ExporterTargetSettingsMixin:
    """Mixin for common exporter setting subpanel functionality.

    Panels that inherit from this mixin need to have a arm_target
    variable for polling."""
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_parent_id = 'ARM_PT_ArmoryExporterPanel'

    # Override this in sub classes
    arm_panel = ''

    @classmethod
    def poll(cls, context):
        wrd = bpy.data.worlds['Arm']
        if (len(wrd.arm_exporterlist) > 0) and (wrd.arm_exporterlist_index >= 0):
            item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
            return item.arm_project_target == cls.arm_target
        return False

    def draw_header(self, context):
        self.layout.label(text='', icon='SETTINGS')

class ARM_PT_ArmoryExporterAndroidSettingsPanel(ExporterTargetSettingsMixin, bpy.types.Panel):
    bl_label = "Android Settings"
    arm_target = 'android-hl'  # See ExporterTargetSettingsMixin

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        col = layout.column()
        col.prop(wrd, 'arm_winorient')
        col.prop(wrd, 'arm_project_android_sdk_min')
        col.prop(wrd, 'arm_project_android_sdk_target')
        col.prop(wrd, 'arm_project_android_sdk_compile')

class ARM_PT_ArmoryExporterAndroidPermissionsPanel(bpy.types.Panel):
    bl_label = "Permissions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ArmoryExporterAndroidSettingsPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        # Permission
        row = layout.row()
        rows = 2
        if len(wrd.arm_exporter_android_permission_list) > 1:
            rows = 4
        row.template_list("ARM_UL_Exporter_AndroidPermissionList", "The_List", wrd, "arm_exporter_android_permission_list", wrd, "arm_exporter_android_permission_list_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_exporter_android_permission_list.new_item", icon='ADD', text="")
        col.operator("arm_exporter_android_permission_list.delete_item", icon='REMOVE', text="")
        row = layout.row()

        if wrd.arm_exporter_android_permission_list_index >= 0 and len(wrd.arm_exporter_android_permission_list) > 0:
            item = wrd.arm_exporter_android_permission_list[wrd.arm_exporter_android_permission_list_index]
            row = layout.row()
            row.prop(item, 'arm_android_permissions')

class ARM_PT_ArmoryExporterAndroidAbiPanel(bpy.types.Panel):
    bl_label = "Android ABI Filters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = { 'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ArmoryExporterAndroidSettingsPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        # ABIs
        row = layout.row()
        rows = 2
        if len(wrd.arm_exporter_android_abi_list) > 1:
            rows = 4
        row.template_list("ARM_UL_Exporter_AndroidAbiList", "The_List", wrd, "arm_exporter_android_abi_list", wrd, "arm_exporter_android_abi_list_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_exporter_android_abi_list.new_item", icon='ADD', text="")
        col.operator("arm_exporter_android_abi_list.delete_item", icon='REMOVE', text="")
        row = layout.row()

        if wrd.arm_exporter_android_abi_list_index >= 0 and len(wrd.arm_exporter_android_abi_list) > 0:
            item = wrd.arm_exporter_android_abi_list[wrd.arm_exporter_android_abi_list_index]
            row = layout.row()
            row.prop(item, 'arm_android_abi')

class ARM_PT_ArmoryExporterAndroidBuildAPKPanel(bpy.types.Panel):
    bl_label = "Building APK"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ArmoryExporterAndroidSettingsPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        path = arm.utils.get_android_sdk_root_path()

        col = layout.column()

        row = col.row()
        row.enabled = len(path) > 0
        row.prop(wrd, 'arm_project_android_build_apk')

        row = col.row()
        row.enabled = wrd.arm_project_android_build_apk
        row.prop(wrd, 'arm_project_android_rename_apk')
        row = col.row()
        row.enabled = wrd.arm_project_android_build_apk and len(arm.utils.get_android_apk_copy_path()) > 0
        row.prop(wrd, 'arm_project_android_copy_apk')

        row = col.row(align=True)
        row.prop(wrd, 'arm_project_android_list_avd')
        sub = row.column(align=True)
        sub.enabled = len(path) > 0
        sub.operator('arm.update_list_android_emulator', text='', icon='FILE_REFRESH')
        sub = row.column(align=True)
        sub.enabled = len(path) > 0 and len(arm.utils.get_android_emulator_name()) > 0
        sub.operator('arm.run_android_emulator', text='', icon='PLAY')

        row = col.row()
        row.enabled = arm.utils.get_project_android_build_apk() and len(arm.utils.get_android_emulator_name()) > 0
        row.prop(wrd, 'arm_project_android_run_avd')

class ARM_PT_ArmoryExporterHTML5SettingsPanel(ExporterTargetSettingsMixin, bpy.types.Panel):
    bl_label = "HTML5 Settings"
    arm_target = 'html5'  # See ExporterTargetSettingsMixin

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        col = layout.column()
        col.prop(wrd, 'arm_project_html5_popupmenu_in_browser')
        row = col.row()
        row.enabled = len(arm.utils.get_html5_copy_path()) > 0
        row.prop(wrd, 'arm_project_html5_copy')
        row = col.row()
        row.enabled = len(arm.utils.get_html5_copy_path()) > 0 and wrd.arm_project_html5_copy and len(arm.utils.get_link_web_server()) > 0
        row.prop(wrd, 'arm_project_html5_start_browser')


class ARM_PT_ArmoryExporterWindowsSettingsPanel(ExporterTargetSettingsMixin, bpy.types.Panel):
    bl_label = "Windows Settings"
    arm_target = 'windows-hl'  # See ExporterTargetSettingsMixin

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        is_windows = arm.utils.get_os_is_windows()

        col = layout.column()
        col.prop(wrd, 'arm_project_win_list_vs')
        row = col.row()
        row.enabled = is_windows
        row.prop(wrd, 'arm_project_win_build', text='After Publish')

        layout = layout.column()
        layout.enabled = is_windows

        if is_windows and wrd.arm_project_win_build != 'nothing' and not arm.utils_vs.is_version_installed(wrd.arm_project_win_list_vs):
            box = draw_error_box(
                layout,
                'The selected version of Visual Studio could not be found and'
                ' may not be installed. The "After Publish" action may not work'
                ' as intended.'
            )
            box.operator('arm.update_list_installed_vs', icon='FILE_REFRESH')

        layout.separator()

        col = layout.column()
        col.enabled = wrd.arm_project_win_build.startswith('compile')
        col.prop(wrd, 'arm_project_win_build_mode')
        col.prop(wrd, 'arm_project_win_build_arch')
        col.prop(wrd, 'arm_project_win_build_log')
        col.prop(wrd, 'arm_project_win_build_cpu')
        col.prop(wrd, 'arm_project_win_build_open')

class ARM_PT_ArmoryProjectPanel(bpy.types.Panel):
    bl_label = "Armory Project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row(align=True)
        row.operator("arm.open_editor", icon="DESKTOP")
        row.operator("arm.open_project_folder", icon="FILE_FOLDER")

class ARM_PT_ProjectFlagsPanel(bpy.types.Panel):
    bl_label = "Flags"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_parent_id = "ARM_PT_ArmoryProjectPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        col = layout.column(heading='Debug', align=True)
        col.prop(wrd, 'arm_verbose_output')
        col.prop(wrd, 'arm_cache_build')
        col.prop(wrd, 'arm_clear_on_compile')
        col.prop(wrd, 'arm_assert_level')
        col.prop(wrd, 'arm_assert_quit')

        col = layout.column(heading='Runtime', align=True)
        col.prop(wrd, 'arm_live_patch')
        col.prop(wrd, 'arm_stream_scene')
        col.prop(wrd, 'arm_loadscreen')
        col.prop(wrd, 'arm_write_config')

        col = layout.column(heading='Renderer', align=True)
        col.prop(wrd, 'arm_batch_meshes')
        col.prop(wrd, 'arm_batch_materials')
        col.prop(wrd, 'arm_deinterleaved_buffers')
        col.prop(wrd, 'arm_export_tangents')

        col = layout.column(heading='Quality')
        row = col.row()  # To expand below property UI horizontally
        row.prop(wrd, 'arm_canvas_img_scaling_quality', expand=True)
        col.prop(wrd, 'arm_texture_quality')
        col.prop(wrd, 'arm_sound_quality')

        col = layout.column(heading='External Assets')
        col.prop(wrd, 'arm_copy_override')
        col.operator('arm.copy_to_bundled', icon='IMAGE_DATA')

class ARM_PT_ProjectFlagsDebugConsolePanel(bpy.types.Panel):
    bl_label = "Debug Console"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ProjectFlagsPanel"

    def draw_header(self, context):
        wrd = bpy.data.worlds['Arm']
        self.layout.prop(wrd, 'arm_debug_console', text='')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        col = layout.column()
        col.enabled = wrd.arm_debug_console
        col.prop(wrd, 'arm_debug_console_position')
        col.prop(wrd, 'arm_debug_console_scale')
        col.prop(wrd, 'arm_debug_console_visible')
        col.prop(wrd, 'arm_debug_console_trace_pos')

class ARM_PT_ProjectWindowPanel(bpy.types.Panel):
    bl_label = "Window"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ArmoryProjectPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        layout.prop(wrd, 'arm_winmode')

        col = layout.column(align=True)
        col.prop(wrd, 'arm_winresize')
        sub = col.column()
        sub.enabled = wrd.arm_winresize
        sub.prop(wrd, 'arm_winmaximize')
        col.enabled = True
        col.prop(wrd, 'arm_winminimize')

        layout.prop(wrd, 'arm_vsync')

class ARM_PT_ProjectModulesPanel(bpy.types.Panel):
    bl_label = "Modules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ArmoryProjectPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        layout.prop(wrd, 'arm_audio')
        layout.prop(wrd, 'arm_physics')
        if wrd.arm_physics != 'Disabled':
            layout.prop(wrd, 'arm_physics_engine')
        layout.prop(wrd, 'arm_navigation')
        if wrd.arm_navigation != 'Disabled':
            layout.prop(wrd, 'arm_navigation_engine')
        layout.prop(wrd, 'arm_ui')
        layout.prop(wrd, 'arm_network')

        layout.prop_search(wrd, 'arm_khafile', bpy.data, 'texts')
        layout.prop(wrd, 'arm_project_root')

class ArmVirtualInputPanel(bpy.types.Panel):
    bl_label = "Armory Virtual Input"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

class ArmoryPlayButton(bpy.types.Operator):
    '''Launch player in new window'''
    bl_idname = 'arm.play'
    bl_label = 'Play'

    def invoke(self, context, event):
        if event.shift:
            state.is_play = True
            make.build_success()
            return{'FINISHED'}
        return self.execute(context)

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']

        if state.proc_build is not None:
            return {"CANCELLED"}

        arm.utils.check_blender_version(self)

        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        arm.utils.check_projectpath(None)

        arm.utils.check_default_props()

        assets.invalidate_enabled = False
        if wrd.arm_clear_on_compile:
            os.system("cls")
        make.play()
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryStopButton(bpy.types.Operator):
    '''Stop currently running player'''
    bl_idname = 'arm.stop'
    bl_label = 'Stop'

    def execute(self, context):
        if state.proc_play != None:
            state.proc_play.terminate()
            state.proc_play = None
        elif state.proc_build != None:
            state.proc_build.terminate()
            state.proc_build = None

        arm.write_probes.check_last_cmft_time()

        return {'FINISHED'}

class ArmoryBuildProjectButton(bpy.types.Operator):
    """Build and compile project"""
    bl_idname = 'arm.build_project'
    bl_label = 'Build'

    @classmethod
    def poll(cls, context):
        wrd = bpy.data.worlds['Arm']
        return wrd.arm_exporterlist_index >= 0 and len(wrd.arm_exporterlist) > 0

    def execute(self, context):
        arm.utils.check_blender_version(self)

        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        arm.utils.check_projectpath(self)

        arm.utils.check_default_props()

        wrd = bpy.data.worlds['Arm']
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        if item.arm_project_rp == '':
            item.arm_project_rp = wrd.arm_rplist[wrd.arm_rplist_index].name
        if item.arm_project_scene == None:
            item.arm_project_scene = context.scene
        # Assume unique rp names
        rplist_index = wrd.arm_rplist_index
        for i in range(0, len(wrd.arm_rplist)):
            if wrd.arm_rplist[i].name == item.arm_project_rp:
                wrd.arm_rplist_index = i
                break
        assets.invalidate_shader_cache(None, None)
        assets.invalidate_enabled = False
        if wrd.arm_clear_on_compile:
            os.system("cls")
        make.build(item.arm_project_target, is_export=True)
        make.compile()
        wrd.arm_rplist_index = rplist_index
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryPublishProjectButton(bpy.types.Operator):
    """Build project ready for publishing."""
    bl_idname = 'arm.publish_project'
    bl_label = 'Publish'

    @classmethod
    def poll(cls, context):
        wrd = bpy.data.worlds['Arm']
        return wrd.arm_exporterlist_index >= 0 and len(wrd.arm_exporterlist) > 0

    def execute(self, context):
        arm.utils.check_blender_version(self)

        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        self.report({'INFO'}, 'Publishing project, check console for details.')

        arm.utils.check_projectpath(self)

        arm.utils.check_default_props()

        wrd = bpy.data.worlds['Arm']
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        if item.arm_project_rp == '':
            item.arm_project_rp = wrd.arm_rplist[wrd.arm_rplist_index].name
        if item.arm_project_scene == None:
            item.arm_project_scene = context.scene
        # Assume unique rp names
        rplist_index = wrd.arm_rplist_index
        for i in range(0, len(wrd.arm_rplist)):
            if wrd.arm_rplist[i].name == item.arm_project_rp:
                wrd.arm_rplist_index = i
                break

        make.clean()
        assets.invalidate_enabled = False
        if wrd.arm_clear_on_compile:
            os.system("cls")
        make.build(item.arm_project_target, is_publish=True, is_export=True)
        make.compile()
        wrd.arm_rplist_index = rplist_index
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryOpenProjectFolderButton(bpy.types.Operator):
    '''Open project folder'''
    bl_idname = 'arm.open_project_folder'
    bl_label = 'Project Folder'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        arm.utils.open_folder(arm.utils.get_fp())
        return{'FINISHED'}

class ArmoryOpenEditorButton(bpy.types.Operator):
    '''Launch this project in the IDE'''
    bl_idname = 'arm.open_editor'
    bl_label = 'Code Editor'
    bl_description = 'Open Project in IDE'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        arm.utils.check_default_props()

        if not os.path.exists(arm.utils.get_fp() + "/khafile.js"):
            print('Generating Krom project for IDE build configuration')
            make.build('krom')

        arm.utils.open_editor()
        return{'FINISHED'}

class CleanMenu(bpy.types.Menu):
    bl_label = "Ok?"
    bl_idname = "OBJECT_MT_clean_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("arm.clean_project")

class CleanButtonMenu(bpy.types.Operator):
    '''Clean cached data'''
    bl_label = "Clean"
    bl_idname = "arm.clean_menu"

    def execute(self, context):
        bpy.ops.wm.call_menu(name=CleanMenu.bl_idname)
        return {"FINISHED"}

class ArmoryCleanProjectButton(bpy.types.Operator):
    '''Delete all cached project data'''
    bl_idname = 'arm.clean_project'
    bl_label = 'Clean Project'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        make.clean()
        return{'FINISHED'}

def draw_view3d_header(self, context):
    if state.proc_build is not None:
        self.layout.label(text='Compiling..')
    elif log.info_text != '':
        self.layout.label(text=log.info_text)

def draw_view3d_object_menu(self, context):
    self.layout.separator()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator('arm.copy_traits_to_active')

class ARM_PT_TopbarPanel(bpy.types.Panel):
    bl_label = "Armory Player"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {'INSTANCED'}

    def draw_header(self, context):
        row = self.layout.row(align=True)
        if state.proc_play is None and state.proc_build is None:
            row.operator("arm.play", icon="PLAY", text="")
        else:
            if bpy.app.version < (3, 0, 0):
                row.operator("arm.stop", icon="CANCEL", text="")
            else:
                row.operator("arm.stop", icon="SEQUENCE_COLOR_01", text="")
        row.operator("arm.clean_menu", icon="BRUSH_DATA", text="")
        row.operator("arm.open_editor", icon="DESKTOP", text="")
        row.operator("arm.open_project_folder", icon="FILE_FOLDER", text="")

    def draw(self, context):
        col = self.layout.column()
        wrd = bpy.data.worlds['Arm']

        col.label(text="Armory Launch")
        col.separator()

        col.prop(wrd, 'arm_runtime')
        col.prop(wrd, 'arm_play_camera')
        col.prop(wrd, 'arm_play_scene')
        col.prop_search(wrd, 'arm_play_renderpath', wrd, 'arm_rplist', text='Render Path')
        col.prop(wrd, 'arm_debug_console', text="Debug Console")

def draw_space_topbar(self, context):
    # for some blender reasons, topbar is instanced twice. this avoids doubling the panel
    if context.region.alignment == 'RIGHT':
        self.layout.popover(panel="ARM_PT_TopbarPanel", text="")

class ARM_PT_RenderPathPanel(bpy.types.Panel):
    bl_label = "Armory Render Path"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        rows = 2
        if len(wrd.arm_rplist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ARM_UL_RPList", "The_List", wrd, "arm_rplist", wrd, "arm_rplist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_rplist.new_item", icon='ADD', text="")
        col.operator("arm_rplist.delete_item", icon='REMOVE', text="")

        if len(wrd.arm_rplist) > 1:
            col.separator()
            op = col.operator("arm_rplist.move_item", icon='TRIA_UP', text="")
            op.direction = 'UP'
            op = col.operator("arm_rplist.move_item", icon='TRIA_DOWN', text="")
            op.direction = 'DOWN'

        if wrd.arm_rplist_index < 0 or len(wrd.arm_rplist) == 0:
            return

        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
        if len(arm.api.drivers) > 0:
            layout.prop_search(rpdat, "rp_driver", wrd, "rp_driver_list", text="Driver")
            layout.separator()
            if rpdat.rp_driver != 'Armory' and arm.api.drivers[rpdat.rp_driver]['draw_props'] != None:
                arm.api.drivers[rpdat.rp_driver]['draw_props'](layout)
                return

class ARM_PT_RenderPathRendererPanel(bpy.types.Panel):
    bl_label = "Renderer"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_RenderPathPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.prop(rpdat, 'rp_renderer')
        if rpdat.rp_renderer == 'Forward':
            layout.prop(rpdat, 'rp_depthprepass')
        layout.prop(rpdat, 'arm_material_model')
        layout.prop(rpdat, 'rp_translucency_state')
        layout.prop(rpdat, 'rp_overlays_state')
        layout.prop(rpdat, 'rp_decals_state')
        layout.prop(rpdat, 'rp_blending_state')
        layout.prop(rpdat, 'rp_depth_texture_state')
        layout.prop(rpdat, 'rp_draw_order')
        layout.prop(rpdat, 'arm_samples_per_pixel')
        layout.prop(rpdat, 'arm_texture_filter')
        layout.prop(rpdat, 'rp_sss_state')
        col = layout.column()
        col.enabled = rpdat.rp_sss_state != 'Off'
        col.prop(rpdat, 'arm_sss_width')
        layout.prop(rpdat, 'arm_rp_displacement')
        if rpdat.arm_rp_displacement == 'Tessellation':
            layout.label(text='Mesh')
            layout.prop(rpdat, 'arm_tess_mesh_inner')
            layout.prop(rpdat, 'arm_tess_mesh_outer')
            layout.label(text='Shadow')
            layout.prop(rpdat, 'arm_tess_shadows_inner')
            layout.prop(rpdat, 'arm_tess_shadows_outer')

        layout.prop(rpdat, 'arm_particles')
        layout.separator(factor=0.1)

        col = layout.column()
        col.prop(rpdat, 'arm_skin')
        col = col.column()
        col.enabled = rpdat.arm_skin == 'On'
        col.prop(rpdat, 'arm_use_armature_deform_only')
        col.prop(rpdat, 'arm_skin_max_bones_auto')
        row = col.row()
        row.enabled = not rpdat.arm_skin_max_bones_auto
        row.prop(rpdat, 'arm_skin_max_bones')
        layout.separator(factor=0.1)

        col = layout.column()
        col.prop(rpdat, 'arm_morph_target')
        col = col.column()
        col.enabled = rpdat.arm_morph_target == 'On'
        layout.separator(factor=0.1)

        col = layout.column()
        col.prop(rpdat, "rp_hdr")
        col.prop(rpdat, "rp_stereo")
        col.prop(rpdat, 'arm_culling')
        col.prop(rpdat, 'rp_pp')


class ARM_PT_RenderPathShadowsPanel(bpy.types.Panel):
    bl_label = "Shadows"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_RenderPathPanel"

    def draw_header(self, context):
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
        self.layout.prop(rpdat, "rp_shadows", text="")

    def compute_subdivs(self, max, subdivs):
        l = [max]
        for i in range(subdivs - 1):
            l.append(int(max / 2))
            max = max / 2
        return l

    def tiles_per_light_type(self, rpdat: arm.props_renderpath.ArmRPListItem, light_type: str) -> int:
        if light_type == 'point':
            return 6
        elif light_type == 'spot':
            return 1
        else:
            return int(rpdat.rp_shadowmap_cascades)

    def lights_number_atlas(self, rpdat: arm.props_renderpath.ArmRPListItem, atlas_size: int, shadowmap_size: int, light_type: str) -> int:
        '''Compute number lights that could fit in an atlas'''
        lights = atlas_size / shadowmap_size
        lights *= lights / self.tiles_per_light_type(rpdat, light_type)
        return int(lights)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.enabled = rpdat.rp_shadows
        col = layout.column()
        col.enabled = not rpdat.rp_shadowmap_atlas_single_map or not rpdat.rp_shadowmap_atlas
        col.prop(rpdat, 'rp_shadowmap_cube')
        layout.prop(rpdat, 'rp_shadowmap_cascade')
        layout.prop(rpdat, 'rp_shadowmap_cascades')
        col = layout.column()
        col2 = col.column()
        col2.enabled = rpdat.rp_shadowmap_cascades != '1'
        col2.prop(rpdat, 'arm_shadowmap_split')
        col.prop(rpdat, 'arm_shadowmap_bounds')
        col.prop(rpdat, 'arm_pcfsize')
        layout.separator()

        layout.prop(rpdat, 'rp_shadowmap_atlas')
        colatlas = layout.column()
        colatlas.enabled = rpdat.rp_shadowmap_atlas
        colatlas.prop(rpdat, 'rp_max_lights')
        colatlas.prop(rpdat, 'rp_max_lights_cluster')
        colatlas.prop(rpdat, 'rp_shadowmap_atlas_lod')

        colatlas_lod = colatlas.column()
        colatlas_lod.enabled = rpdat.rp_shadowmap_atlas_lod
        colatlas_lod.prop(rpdat, 'rp_shadowmap_atlas_lod_subdivisions')

        colatlas_lod_info = colatlas_lod.row()
        colatlas_lod_info.alignment = 'RIGHT'
        subdivs_list = self.compute_subdivs(int(rpdat.rp_shadowmap_cascade), int(rpdat.rp_shadowmap_atlas_lod_subdivisions))
        subdiv_text = "Subdivisions for spot lights: " + ', '.join(map(str, subdivs_list))
        colatlas_lod_info.label(text=subdiv_text, icon="IMAGE_ZDEPTH")

        if not rpdat.rp_shadowmap_atlas_single_map:
            colatlas_lod_info = colatlas_lod.row()
            colatlas_lod_info.alignment = 'RIGHT'
            subdivs_list = self.compute_subdivs(int(rpdat.rp_shadowmap_cube), int(rpdat.rp_shadowmap_atlas_lod_subdivisions))
            subdiv_text = "Subdivisions for point lights: " + ', '.join(map(str, subdivs_list))
            colatlas_lod_info.label(text=subdiv_text, icon="IMAGE_ZDEPTH")

        size_warning = int(rpdat.rp_shadowmap_cascade) > 2048 or int(rpdat.rp_shadowmap_cube) > 2048

        colatlas.prop(rpdat, 'rp_shadowmap_atlas_single_map')
        # show size for single texture
        if rpdat.rp_shadowmap_atlas_single_map:
            colatlas_single = colatlas.column()
            colatlas_single.prop(rpdat, 'rp_shadowmap_atlas_max_size')
            if rpdat.rp_shadowmap_atlas_max_size != '':
                atlas_size = int(rpdat.rp_shadowmap_atlas_max_size)
                shadowmap_size = int(rpdat.rp_shadowmap_cascade)

                if shadowmap_size > 2048:
                    size_warning = True

                point_lights = self.lights_number_atlas(rpdat, atlas_size, shadowmap_size, 'point')
                spot_lights = self.lights_number_atlas(rpdat, atlas_size, shadowmap_size, 'spot')
                dir_lights = self.lights_number_atlas(rpdat, atlas_size, shadowmap_size, 'sun')

                col = colatlas_single.row()
                col.alignment = 'RIGHT'
                col.label(text=f'Enough space for { point_lights } point lights or { spot_lights } spot lights or { dir_lights } directional lights.')
        else:
            # show size for all types
            colatlas_mixed = colatlas.column()
            colatlas_mixed.prop(rpdat, 'rp_shadowmap_atlas_max_size_spot')

            if rpdat.rp_shadowmap_atlas_max_size_spot != '':
                atlas_size = int(rpdat.rp_shadowmap_atlas_max_size_spot)
                shadowmap_size = int(rpdat.rp_shadowmap_cascade)
                spot_lights = self.lights_number_atlas(rpdat, atlas_size, shadowmap_size, 'spot')

                if shadowmap_size > 2048:
                    size_warning = True

                col = colatlas_mixed.row()
                col.alignment = 'RIGHT'
                col.label(text=f'Enough space for {spot_lights} spot lights.')

            colatlas_mixed.prop(rpdat, 'rp_shadowmap_atlas_max_size_point')

            if rpdat.rp_shadowmap_atlas_max_size_point != '':
                atlas_size = int(rpdat.rp_shadowmap_atlas_max_size_point)
                shadowmap_size = int(rpdat.rp_shadowmap_cube)
                point_lights = self.lights_number_atlas(rpdat, atlas_size, shadowmap_size, 'point')

                if shadowmap_size > 2048:
                    size_warning = True

                col = colatlas_mixed.row()
                col.alignment = 'RIGHT'
                col.label(text=f'Enough space for {point_lights} point lights.')

            colatlas_mixed.prop(rpdat, 'rp_shadowmap_atlas_max_size_sun')

            if rpdat.rp_shadowmap_atlas_max_size_sun != '':
                atlas_size = int(rpdat.rp_shadowmap_atlas_max_size_sun)
                shadowmap_size = int(rpdat.rp_shadowmap_cascade)
                dir_lights = self.lights_number_atlas(rpdat, atlas_size, shadowmap_size, 'sun')

                if shadowmap_size > 2048:
                    size_warning = True

                col = colatlas_mixed.row()
                col.alignment = 'RIGHT'
                col.label(text=f'Enough space for {dir_lights} directional lights.')

        # show warning when user picks a size higher than 2048 (arbitrary number).
        if size_warning:
            col = layout.column()
            row = col.row()
            row.alignment = 'RIGHT'
            row.label(text='Warning: Game will crash if texture size is higher than max texture size allowed by target.', icon='ERROR')

class ARM_PT_RenderPathVoxelsPanel(bpy.types.Panel):
    bl_label = "Voxels"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_RenderPathPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.prop(rpdat, 'rp_voxels')
        col = layout.column()
        col.enabled = rpdat.rp_voxels != 'Off'
        col2 = col.column()
        col2.enabled = rpdat.rp_voxels == 'Voxel GI'
        col3 = col.column()
        col3.enabled = rpdat.rp_voxels == 'Voxel AO'
        col.prop(rpdat, 'arm_voxelgi_shadows', text='Shadows')
        #col2.prop(rpdat, 'arm_voxelgi_refraction', text='Refraction')
        #col2.prop(rpdat, 'arm_voxelgi_bounces')
        col.prop(rpdat, 'arm_voxelgi_clipmap_count')
        #col.prop(rpdat, 'arm_voxelgi_cones')
        col.prop(rpdat, 'rp_voxelgi_resolution')
        #col.prop(rpdat, 'rp_voxelgi_resolution_z')
        col2.enabled = rpdat.rp_voxels == 'Voxel GI'
        #col.prop(rpdat, 'arm_voxelgi_temporal')
        col.label(text="Light")
        col2 = col.column()
        col2.enabled = rpdat.rp_voxels == 'Voxel GI'
        col2.prop(rpdat, 'arm_voxelgi_diff')
        col2.prop(rpdat, 'arm_voxelgi_spec')
        #col2.prop(rpdat, 'arm_voxelgi_refr')
        col.prop(rpdat, 'arm_voxelgi_occ')
        col.label(text="Ray")
        col.prop(rpdat, 'arm_voxelgi_size')
        col.prop(rpdat, 'arm_voxelgi_step')
        col.prop(rpdat, 'arm_voxelgi_range')
        #col.prop(rpdat, 'arm_voxelgi_offset')
        #col.prop(rpdat, 'arm_voxelgi_aperture')

class ARM_PT_RenderPathWorldPanel(bpy.types.Panel):
    bl_label = "World"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_RenderPathPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.prop(rpdat, "rp_background")

        col = layout.column()
        col.prop(rpdat, 'arm_irradiance')
        colb = col.column()
        colb.enabled = rpdat.arm_irradiance
        colb.prop(rpdat, 'arm_radiance')
        sub = colb.row()
        sub.enabled = rpdat.arm_radiance
        sub.prop(rpdat, 'arm_radiance_size')
        layout.separator()

        layout.prop(rpdat, 'arm_clouds')

        col = layout.column(align=True)
        col.prop(rpdat, "rp_water")
        col = col.column(align=True)
        col.enabled = rpdat.rp_water
        col.prop(rpdat, 'arm_water_level')
        col.prop(rpdat, 'arm_water_density')
        col.prop(rpdat, 'arm_water_displace')
        col.prop(rpdat, 'arm_water_speed')
        col.prop(rpdat, 'arm_water_freq')
        col.prop(rpdat, 'arm_water_refract')
        col.prop(rpdat, 'arm_water_reflect')
        col.prop(rpdat, 'arm_water_color')

class ARM_PT_RenderPathPostProcessPanel(bpy.types.Panel):
    bl_label = "Post Process"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_RenderPathPanel"

    def draw_header(self, context):
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
        self.layout.prop(rpdat, "rp_render_to_texture", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.enabled = rpdat.rp_render_to_texture
        col = layout.column()
        col.prop(rpdat, "rp_antialiasing")
        col.prop(rpdat, "rp_supersampling")

        col = layout.column()
        col.prop(rpdat, 'arm_rp_resolution')
        if rpdat.arm_rp_resolution == 'Custom':
            col.prop(rpdat, 'arm_rp_resolution_size')
            col.prop(rpdat, 'arm_rp_resolution_filter')
        col.prop(rpdat, 'rp_dynres')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_ssgi")
        sub = col.column()
        sub.enabled = rpdat.rp_ssgi != 'Off'
        sub.prop(rpdat, 'arm_ssgi_half_res')
        sub.prop(rpdat, 'arm_ssgi_rays')
        sub.prop(rpdat, 'arm_ssgi_radius')
        sub.prop(rpdat, 'arm_ssgi_strength')
        sub.prop(rpdat, 'arm_ssgi_max_steps')
        layout.separator()

        row = layout.row()
        row.enabled = rpdat.arm_material_model == 'Full'
        row.prop(rpdat, 'arm_micro_shadowing')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_ssr")
        col.prop(rpdat, 'arm_ssr_half_res')
        col = col.column()
        col.enabled = rpdat.rp_ssr
        col.prop(rpdat, 'arm_ssr_ray_step')
        col.prop(rpdat, 'arm_ssr_search_dist')
        col.prop(rpdat, 'arm_ssr_falloff_exp')
        col.prop(rpdat, 'arm_ssr_jitter')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_ss_refraction")
        col = col.column()
        col.enabled = rpdat.rp_ss_refraction
        col.prop(rpdat, 'arm_ss_refraction_ray_step')
        col.prop(rpdat, 'arm_ss_refraction_search_dist')
        col.prop(rpdat, 'arm_ss_refraction_falloff_exp')
        col.prop(rpdat, 'arm_ss_refraction_jitter')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, 'arm_ssrs')
        col = col.column()
        col.enabled = rpdat.arm_ssrs
        col.prop(rpdat, 'arm_ssrs_ray_step')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_bloom")
        _col = col.column()
        _col.enabled = rpdat.rp_bloom
        _col.prop(rpdat, 'arm_bloom_follow_blender')
        if not rpdat.arm_bloom_follow_blender:
            _col.prop(rpdat, 'arm_bloom_threshold')
            _col.prop(rpdat, 'arm_bloom_knee')
            _col.prop(rpdat, 'arm_bloom_radius')
            _col.prop(rpdat, 'arm_bloom_strength')
        _col.prop(rpdat, 'arm_bloom_quality')
        _col.prop(rpdat, 'arm_bloom_anti_flicker')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_motionblur")
        col = col.column()
        col.enabled = rpdat.rp_motionblur != 'Off'
        col.prop(rpdat, 'arm_motion_blur_intensity')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_volumetriclight")
        col = col.column()
        col.enabled = rpdat.rp_volumetriclight
        col.prop(rpdat, 'arm_volumetric_light_air_color')
        col.prop(rpdat, 'arm_volumetric_light_air_turbidity')
        col.prop(rpdat, 'arm_volumetric_light_steps')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_chromatic_aberration")
        col = col.column()
        col.enabled = rpdat.rp_chromatic_aberration
        col.prop(rpdat, 'arm_chromatic_aberration_type')
        col.prop(rpdat, 'arm_chromatic_aberration_strength')
        if rpdat.arm_chromatic_aberration_type == "Spectral":
            col.prop(rpdat, 'arm_chromatic_aberration_samples')

class ARM_PT_RenderPathCompositorPanel(bpy.types.Panel):
    bl_label = "Compositor"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_RenderPathPanel"

    def draw_header(self, context):
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
        self.layout.prop(rpdat, "rp_compositornodes", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.enabled = rpdat.rp_compositornodes
        layout.prop(rpdat, 'arm_tonemap')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, 'arm_letterbox')
        col = col.column(align=True)
        col.enabled = rpdat.arm_letterbox
        col.prop(rpdat, 'arm_letterbox_color')
        col.prop(rpdat, 'arm_letterbox_size')
        layout.separator()

        col = layout.column()
        draw_conditional_prop(col, 'Distort', rpdat, 'arm_distort', 'arm_distort_strength')
        draw_conditional_prop(col, 'Film Grain', rpdat, 'arm_grain', 'arm_grain_strength')
        draw_conditional_prop(col, 'Sharpen', rpdat, 'arm_sharpen', 'arm_sharpen_strength')
        draw_conditional_prop(col, 'Vignette', rpdat, 'arm_vignette', 'arm_vignette_strength')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, 'arm_fog')
        col = col.column(align=True)
        col.enabled = rpdat.arm_fog
        col.prop(rpdat, 'arm_fog_color')
        col.prop(rpdat, 'arm_fog_amounta')
        col.prop(rpdat, 'arm_fog_amountb')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, "rp_autoexposure")
        sub = col.column(align=True)
        sub.enabled = rpdat.rp_autoexposure
        sub.prop(rpdat, 'arm_autoexposure_strength', text='Strength')
        sub.prop(rpdat, 'arm_autoexposure_speed', text='Speed')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, 'arm_fisheye')
        col.prop(rpdat, 'arm_lensflare')
        layout.separator()

        col = layout.column()
        col.prop(rpdat, 'arm_lens')
        col = col.column(align=True)
        col.enabled = rpdat.arm_lens
        col.prop(rpdat, 'arm_lens_texture')
        if rpdat.arm_lens_texture != "":
            col.prop(rpdat, 'arm_lens_texture_masking')
            if rpdat.arm_lens_texture_masking:
                sub = col.column(align=True)
                sub.prop(rpdat, 'arm_lens_texture_masking_centerMinClip')
                sub.prop(rpdat, 'arm_lens_texture_masking_centerMaxClip')
                sub = col.column(align=True)
                sub.prop(rpdat, 'arm_lens_texture_masking_luminanceMin')
                sub.prop(rpdat, 'arm_lens_texture_masking_luminanceMax')
                col.prop(rpdat, 'arm_lens_texture_masking_brightnessExp')
                layout.separator()
        layout.separator()

        col = layout.column()
        col.prop(rpdat, 'arm_lut')
        col = col.column(align=True)
        col.enabled = rpdat.arm_lut
        col.prop(rpdat, 'arm_lut_texture')
        layout.separator()

class ARM_PT_BakePanel(bpy.types.Panel):
    bl_label = "Armory Bake"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scn = bpy.data.scenes[context.scene.name]

        row = layout.row(align=True)
        row.prop(scn, "arm_bakemode", expand=True)

        if scn.arm_bakemode == "Static Map":

            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("arm.bake_textures", icon="RENDER_STILL")
            row.operator("arm.bake_apply")

            col = layout.column()
            col.prop(scn, 'arm_bakelist_scale')
            col.prop(scn.cycles, "samples")

            layout.prop(scn, 'arm_bakelist_unwrap')

            rows = 2
            if len(scn.arm_bakelist) > 1:
                rows = 4
            row = layout.row()
            row.template_list("ARM_UL_BakeList", "The_List", scn, "arm_bakelist", scn, "arm_bakelist_index", rows=rows)
            col = row.column(align=True)
            col.operator("arm_bakelist.new_item", icon='ADD', text="")
            col.operator("arm_bakelist.delete_item", icon='REMOVE', text="")
            col.menu("ARM_MT_BakeListSpecials", icon='DOWNARROW_HLT', text="")

            if len(scn.arm_bakelist) > 1:
                col.separator()
                op = col.operator("arm_bakelist.move_item", icon='TRIA_UP', text="")
                op.direction = 'UP'
                op = col.operator("arm_bakelist.move_item", icon='TRIA_DOWN', text="")
                op.direction = 'DOWN'

            if scn.arm_bakelist_index >= 0 and len(scn.arm_bakelist) > 0:
                item = scn.arm_bakelist[scn.arm_bakelist_index]
                layout.prop_search(item, "obj", bpy.data, "objects", text="Object")
                layout.prop(item, "res_x")
                layout.prop(item, "res_y")

class ArmGenLodButton(bpy.types.Operator):
    """Automatically generate LoD levels."""
    bl_idname = 'arm.generate_lod'
    bl_label = 'Auto Generate'

    def lod_name(self, name, level):
        return name + '_LOD' + str(level + 1)

    def execute(self, context):
        obj = context.object
        if obj == None:
            return{'CANCELLED'}

        # Clear
        mdata = context.object.data
        mdata.arm_lodlist_index = 0
        mdata.arm_lodlist.clear()

        # Lod levels
        wrd = bpy.data.worlds['Arm']
        ratio = wrd.arm_lod_gen_ratio
        num_levels = wrd.arm_lod_gen_levels
        for level in range(0, num_levels):
            new_obj = obj.copy()
            for i in range(0, 3):
                new_obj.location[i] = 0
                new_obj.rotation_euler[i] = 0
                new_obj.scale[i] = 1
            new_obj.data = obj.data.copy()
            new_obj.name = self.lod_name(obj.name, level)
            new_obj.parent = obj
            new_obj.hide_viewport = True
            new_obj.hide_render = True
            mod = new_obj.modifiers.new('Decimate', 'DECIMATE')
            mod.ratio = ratio
            ratio *= wrd.arm_lod_gen_ratio
            context.scene.collection.objects.link(new_obj)

        # Screen sizes
        for level in range(0, num_levels):
            mdata.arm_lodlist.add()
            mdata.arm_lodlist[-1].name = self.lod_name(obj.name, level)
            mdata.arm_lodlist[-1].screen_size_prop = (1 - (1 / (num_levels + 1)) * level) - (1 / (num_levels + 1))

        return{'FINISHED'}

class ARM_PT_LodPanel(bpy.types.Panel):
    bl_label = "Armory Lod"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        obj = bpy.context.object

        # Mesh only for now
        if obj.type != 'MESH':
            return

        mdata = obj.data

        rows = 2
        if len(mdata.arm_lodlist) > 1:
            rows = 4

        row = layout.row()
        row.template_list("ARM_UL_LodList", "The_List", mdata, "arm_lodlist", mdata, "arm_lodlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_lodlist.new_item", icon='ADD', text="")
        col.operator("arm_lodlist.delete_item", icon='REMOVE', text="")

        if len(mdata.arm_lodlist) > 1:
            col.separator()
            op = col.operator("arm_lodlist.move_item", icon='TRIA_UP', text="")
            op.direction = 'UP'
            op = col.operator("arm_lodlist.move_item", icon='TRIA_DOWN', text="")
            op.direction = 'DOWN'

        if mdata.arm_lodlist_index >= 0 and len(mdata.arm_lodlist) > 0:
            item = mdata.arm_lodlist[mdata.arm_lodlist_index]
            layout.prop_search(item, "name", bpy.data, "objects", text="Object")
            layout.prop(item, "screen_size_prop")
        layout.prop(mdata, "arm_lod_material")

        # Auto lod for meshes
        if obj.type == 'MESH':
            layout.separator()
            layout.operator("arm.generate_lod")
            wrd = bpy.data.worlds['Arm']
            layout.prop(wrd, 'arm_lod_gen_levels')
            layout.prop(wrd, 'arm_lod_gen_ratio')

class ArmGenTerrainButton(bpy.types.Operator):
    '''Generate terrain sectors'''
    bl_idname = 'arm.generate_terrain'
    bl_label = 'Generate'

    def execute(self, context):
        scn = context.scene
        if scn == None:
            return{'CANCELLED'}
        sectors = scn.arm_terrain_sectors
        size = scn.arm_terrain_sector_size
        height_scale = scn.arm_terrain_height_scale

        # Create material
        mat = bpy.data.materials.new(name="Terrain")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        node = nodes.new('ShaderNodeDisplacement')
        node.location = (-200, 100)
        node.inputs[2].default_value = height_scale
        node.space = 'WORLD'
        links.new(nodes['Material Output'].inputs[2], node.outputs[0])
        node = nodes.new('ShaderNodeTexImage')
        node.location = (-600, 100)
        node.interpolation = 'Closest'
        node.extension = 'EXTEND'
        node.arm_material_param = True
        node.name = '_TerrainHeight'
        node.label = '_TerrainHeight' # Height-map texture link for this sector
        links.new(nodes['Displacement'].inputs[0], nodes['_TerrainHeight'].outputs[0])
        node = nodes.new('ShaderNodeBump')
        node.location = (-200, -200)
        node.inputs[0].default_value = 5.0
        links.new(nodes['Bump'].inputs[2], nodes['_TerrainHeight'].outputs[0])
        links.new(nodes['Principled BSDF'].inputs[20], nodes['Bump'].outputs[0])

        # Create sectors
        root_obj = bpy.data.objects.new("Terrain", None)
        root_obj.location[0] = 0
        root_obj.location[1] = 0
        root_obj.location[2] = 0
        root_obj.arm_export = False
        scn.collection.objects.link(root_obj)
        scn.arm_terrain_object = root_obj

        for i in range(sectors[0] * sectors[1]):
            j = str(i + 1).zfill(2)
            x = i % sectors[0]
            y = int(i / sectors[0])
            bpy.ops.mesh.primitive_plane_add(location=(x * size, -y * size, 0))
            slice_obj = bpy.context.active_object
            slice_obj.scale[0] = size / 2
            slice_obj.scale[1] = -(size / 2)
            slice_obj.scale[2] = height_scale
            slice_obj.data.materials.append(mat)
            for p in slice_obj.data.polygons:
                p.use_smooth = True
            slice_obj.name = 'Terrain.' + j
            slice_obj.parent = root_obj
            sub_mod = slice_obj.modifiers.new('Subdivision', 'SUBSURF')
            sub_mod.subdivision_type = 'SIMPLE'
            disp_mod = slice_obj.modifiers.new('Displace', 'DISPLACE')
            disp_mod.texture_coords = 'UV'
            disp_mod.texture = bpy.data.textures.new(name='Terrain.' + j, type='IMAGE')
            disp_mod.texture.extension = 'EXTEND'
            disp_mod.texture.use_interpolation = False
            disp_mod.texture.use_mipmap = False
            disp_mod.texture.image = bpy.data.images.load(filepath=scn.arm_terrain_textures+'/heightmap_' + j + '.png')
            f = 1
            levels = 0
            while f < disp_mod.texture.image.size[0]:
                f *= 2
                levels += 1
            sub_mod.levels = sub_mod.render_levels = levels

        return{'FINISHED'}

class ARM_PT_TerrainPanel(bpy.types.Panel):
    bl_label = "Armory Terrain"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scn = bpy.context.scene
        if scn == None:
            return
        layout.prop(scn, 'arm_terrain_textures')
        layout.prop(scn, 'arm_terrain_sectors')
        layout.prop(scn, 'arm_terrain_sector_size')
        layout.prop(scn, 'arm_terrain_height_scale')
        layout.operator('arm.generate_terrain')
        layout.prop(scn, 'arm_terrain_object')

class ARM_PT_TilesheetPanel(bpy.types.Panel):
    bl_label = "Armory Tilesheet"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        rows = 2
        if len(wrd.arm_tilesheetlist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ARM_UL_TilesheetList", "The_List", wrd, "arm_tilesheetlist", wrd, "arm_tilesheetlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_tilesheetlist.new_item", icon='ADD', text="")
        col.operator("arm_tilesheetlist.delete_item", icon='REMOVE', text="")

        if len(wrd.arm_tilesheetlist) > 1:
            col.separator()
            op = col.operator("arm_tilesheetlist.move_item", icon='TRIA_UP', text="")
            op.direction = 'UP'
            op = col.operator("arm_tilesheetlist.move_item", icon='TRIA_DOWN', text="")
            op.direction = 'DOWN'

        if wrd.arm_tilesheetlist_index >= 0 and len(wrd.arm_tilesheetlist) > 0:
            dat = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
            layout.prop(dat, "tilesx_prop")
            layout.prop(dat, "tilesy_prop")
            layout.prop(dat, "framerate_prop")

            layout.label(text='Actions')
            rows = 2
            if len(dat.arm_tilesheetactionlist) > 1:
                rows = 4
            row = layout.row()
            row.template_list("ARM_UL_TilesheetList", "The_List", dat, "arm_tilesheetactionlist", dat, "arm_tilesheetactionlist_index", rows=rows)
            col = row.column(align=True)
            col.operator("arm_tilesheetactionlist.new_item", icon='ADD', text="")
            col.operator("arm_tilesheetactionlist.delete_item", icon='REMOVE', text="")

            if len(dat.arm_tilesheetactionlist) > 1:
                col.separator()
                op = col.operator("arm_tilesheetactionlist.move_item", icon='TRIA_UP', text="")
                op.direction = 'UP'
                op = col.operator("arm_tilesheetactionlist.move_item", icon='TRIA_DOWN', text="")
                op.direction = 'DOWN'

            if dat.arm_tilesheetactionlist_index >= 0 and len(dat.arm_tilesheetactionlist) > 0:
                adat = dat.arm_tilesheetactionlist[dat.arm_tilesheetactionlist_index]
                layout.prop(adat, "start_prop")
                layout.prop(adat, "end_prop")
                layout.prop(adat, "loop_prop")

class ArmPrintTraitsButton(bpy.types.Operator):
    bl_idname = 'arm.print_traits'
    bl_label = 'Print All Traits'
    bl_description = 'Returns all traits in current blend'

    def execute(self, context):
        for s in bpy.data.scenes:
            print('Scene: {0}'.format(s.name))
            for t in s.arm_traitlist:
                if not t.enabled_prop:
                    continue
                tname = "undefined"
                if t.type_prop == 'Haxe Script' or "Bundled":
                    tname = t.class_name_prop
                if t.type_prop == 'Logic Nodes':
                    tname = t.node_tree_prop.name
                if t.type_prop == 'UI Canvas':
                    tname = t.canvas_name_prop
                if t.type_prop == 'WebAssembly':
                    tname = t.webassembly_prop
                print('Scene Trait: {0} ("{1}")'.format(s.name, tname))
            for o in s.objects:
                for t in o.arm_traitlist:
                    if not t.enabled_prop:
                        continue
                    tname = "undefined"
                    if t.type_prop == 'Haxe Script' or "Bundled":
                        tname = t.class_name_prop
                    if t.type_prop == 'Logic Nodes':
                        tname = t.node_tree_prop.name
                    if t.type_prop == 'UI Canvas':
                        tname = t.canvas_name_prop
                    if t.type_prop == 'WebAssembly':
                        tname = t.webassembly_prop
                    print(' Object Trait: {0} ("{1}")'.format(o.name, tname))
        return{'FINISHED'}

class ARM_PT_MaterialNodePanel(bpy.types.Panel):
    bl_label = 'Armory Material Node'
    bl_idname = 'ARM_PT_MaterialNodePanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == 'ShaderNodeTree'
                and context.space_data.edit_tree
                and context.space_data.shader_type == 'OBJECT')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        n = context.active_node
        if n != None and (n.bl_idname == 'ShaderNodeRGB' or n.bl_idname == 'ShaderNodeValue' or n.bl_idname == 'ShaderNodeTexImage'):
            layout.prop(context.active_node, 'arm_material_param')

class ARM_OT_CopyToBundled(bpy.types.Operator):
    bl_label = 'Copy To Bundled'
    bl_idname = 'arm.copy_to_bundled'
    bl_description = ('Copies and repaths external image assets to project Bundled folder')

    def execute(self, context):
        self.copy_to_bundled(bpy.data.images)
        return {'FINISHED'}

    @classmethod
    def copy_to_bundled(self, data):
        wrd = bpy.data.worlds['Arm']
        project_path = arm.utils.get_fp()

        # Blend - Images
        for asset in data:
            # File is saved
            if asset.filepath_from_user() != '':
                bundled_filepath = project_path + '/Bundled/' + asset.name
                try:
                    # Exists -> Yes
                    if os.path.isfile(bundled_filepath):
                        # Override -> Yes
                        if (wrd.arm_copy_override):
                            # Valid file
                            if asset.has_data:
                                asset.filepath_raw = bundled_filepath
                                asset.save()
                                asset.reload()
                                # Syntax - Yellow
                                print(log.colorize(f'Asset name "{asset.name}" already exists, overriding the original', 33), file=sys.stderr)
                            # Invalid file or corrupted
                            else:
                                # Syntax - Red
                                log.error(f'Asset name "{asset.name}" has no data to save or copy, skipping')
                                continue
                        # Override -> No
                        else:
                            # Syntax - Yellow
                            print(log.colorize(f'Asset name "{asset.name}" already exists, skipping', 33), file=sys.stderr)
                            continue
                    # Exists -> No
                    else:
                        # Valid file
                        if asset.has_data:
                            asset.filepath_raw = bundled_filepath
                            asset.save()
                            asset.reload()
                            # Syntax - Green
                            print(log.colorize(f'Asset name "{asset.name}" was successfully copied', 32), file=sys.stderr)
                        # Invalid file or corrupted
                        else:
                            # Syntax - Red
                            log.error(f'Asset name "{asset.name}" has no data to save or copy, skipping')
                            continue
                except:
                    # Syntax - Red
                    log.error(f'Insufficient write permissions or other issues occurred')
                    continue
            # File is unsaved
            else:
                # Syntax - Purple
                log.warn(f'Asset name "{asset.name}" is either packed or unsaved, skipping')
                continue

class ARM_OT_ShowFileVersionInfo(bpy.types.Operator):
    bl_label = 'Show old file version info'
    bl_idname = 'arm.show_old_file_version_info'
    bl_description = ('Displays an info panel that warns about opening a file'
                       'which was created in a previous version of Armory')
    bl_options = {'INTERNAL'}

    wrd = None

    def draw_message_box(self, context):
        file_version = ARM_OT_ShowFileVersionInfo.wrd.arm_version
        current_version = props.arm_version


        layout = self.layout
        layout = layout.column(align=True)
        layout.alignment = 'EXPAND'

        if current_version == file_version:
            layout.label('This file was saved in', icon='INFO')
            layout.label('the current Armory version', icon='BLANK1')
            layout.separator()
            layout.label(f'(version: {current_version}')
            row = layout.row(align=True)
            row.active_default = True
            row.operator('arm.discard_popup', text='Ok')

        # this will help order versions better, somewhat.
        # note: this is NOT complete
        current_version = tuple( current_version.split('.') )
        file_version = tuple( file_version.split('.') )

        if current_version > file_version:
            layout.label(text='Warning: This file was saved in a', icon='ERROR')
            layout.label(text='previous version of Armory!', icon='BLANK1')
            layout.separator()

            layout.label(text='Please inform yourself about breaking changes!', icon='BLANK1')
            layout.label(text=f'File saved in: {file_version}', icon='BLANK1')
            layout.label(text=f'Current version: {current_version}', icon='BLANK1')
            layout.separator()
            layout.separator()
            layout.label(text='Should Armory try to automatically update', icon='BLANK1')
            layout.label(text='the file to the current SDK version?', icon='BLANK1')
            layout.separator()

            row = layout.row(align=True)
            row.active_default = True
            row.operator('arm.update_file_sdk', text='Yes')
            row.active_default = False
            row.operator('arm.discard_popup', text='No')
        else:
            layout.label(text='Warning: This file was saved in a', icon='ERROR')
            layout.label(text='future version of Armory!', icon='BLANK1')
            layout.separator()

            layout.label(text='It is impossible to downgrade a file,', icon='BLANK1')
            layout.label(text='Something will probably be broken here.', icon='BLANK1')
            layout.label(text=f'File saved in: {file_version}', icon='BLANK1')
            layout.label(text=f'Current version: {current_version}', icon='BLANK1')
            layout.separator()
            layout.separator()
            layout.label(text='Please check how this file was created', icon='BLANK1')
            layout.separator()

            row = layout.row(align=True)
            row.active_default = True
            row.operator('arm.discard_popup', text='Ok')

    def execute(self, context):
        ARM_OT_ShowFileVersionInfo.wrd = bpy.data.worlds['Arm']
        context.window_manager.popover(ARM_OT_ShowFileVersionInfo.draw_message_box, ui_units_x=16)

        return {"FINISHED"}

class ARM_OT_ShowNodeUpdateErrors(bpy.types.Operator):
    bl_label = 'Show upgrade failure details'
    bl_idname = 'arm.show_node_update_errors'
    bl_description = ('Displays an info panel that shows the different errors that occurred when upgrading nodes')

    wrd = None  # a helper internal variable

    def draw_message_box(self, context):
        list_of_errors = arm.logicnode.replacement.replacement_errors.copy()
        # note: list_of_errors is a set of tuples: `(error_type, node_class, tree_name)`
        # where `error_type` can be "unregistered", "update failed", "future version", "bad version", or "misc."

        file_version = ARM_OT_ShowNodeUpdateErrors.wrd.arm_version
        current_version = props.arm_version

        # this will help order versions better, somewhat.
        # note: this is NOT complete
        current_version_2 = tuple(current_version.split('.'))
        file_version_2 = tuple(file_version.split('.'))
        is_armory_upgrade = (current_version_2 > file_version_2)

        error_types = set()
        errored_trees = set()
        errored_nodes = set()
        for error_entry in list_of_errors:
            error_types.add(error_entry[0])
            errored_nodes.add(error_entry[1])
            errored_trees.add(error_entry[2])

        layout = self.layout
        layout = layout.column(align=True)
        layout.alignment = 'EXPAND'

        layout.label(text="Some nodes failed to be updated to the current Armory version", icon="ERROR")
        if current_version == file_version:
            layout.label(text="(This might be because you are using a development snapshot, or a homemade version ;) )", icon='BLANK1')
        elif not is_armory_upgrade:
            layout.label(text="(Please note that it is not possible do downgrade nodes to a previous version either.", icon='BLANK1')
            layout.label(text="This might be the cause of your problem.)", icon='BLANK1')

        layout.label(text=f'File saved in: {file_version}', icon='BLANK1')
        layout.label(text=f'Current version: {current_version}', icon='BLANK1')
        layout.separator()

        if 'update failed' in error_types:
            layout.label(text="Some nodes do not have an update procedure to deal with the version saved in this file.", icon='BLANK1')
            if current_version == file_version:
                layout.label(text="(if you are a developer, this might be because you didn't implement it yet.)", icon='BLANK1')
        if 'bad version' in error_types:
            layout.label(text="Some nodes do not have version information attached to them.", icon='BLANK1')
        if 'unregistered' in error_types:
            if is_armory_upgrade:
                layout.label(text='Some nodes seem to be too old to be understood by armory anymore', icon='BLANK1')
            else:
                layout.label(text="Some nodes are unknown to armory, either because they are too new or too old.", icon='BLANK1')
        if 'future version' in error_types:
            if is_armory_upgrade:
                layout.label(text='Somehow, some nodes seem to have been created with a future version of armory.', icon='BLANK1')
            else:
                layout.label(text='Some nodes seem to have been created with a future version of armory.', icon='BLANK1')
        if 'misc.' in error_types:
            layout.label(text="Some nodes' update procedure failed to complete")

        layout.separator()
        layout.label(text='the nodes impacted are the following:', icon='BLANK1')
        for node in errored_nodes:
            layout.label(text=f'   {node}', icon='BLANK1')
        layout.separator()
        layout.label(text='the node trees impacted are the following:', icon='BLANK1')
        for tree in errored_trees:
            layout.label(text=f'   "{tree}"', icon='BLANK1')

        layout.separator()
        layout.label(text="A detailed error report has been saved next to the blender file.", icon='BLANK1')
        layout.label(text="the file name is \"node_update_failure\", followed by the current time.", icon='BLANK1')
        layout.separator()

        row = layout.row(align=True)
        row.active_default = False
        row.operator('arm.discard_popup', text='Ok')
        row.operator('arm.open_project_folder', text='Open Project Folder', icon="FILE_FOLDER")

    def execute(self, context):
        ARM_OT_ShowNodeUpdateErrors.wrd = bpy.data.worlds['Arm']
        context.window_manager.popover(ARM_OT_ShowNodeUpdateErrors.draw_message_box, ui_units_x=32)
        return {"FINISHED"}

class ARM_OT_UpdateFileSDK(bpy.types.Operator):
    bl_idname = 'arm.update_file_sdk'
    bl_label = 'Update file to current SDK version'
    bl_description = bl_label
    bl_options = {'INTERNAL'}

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        # This allows for seamless migration from earlier versions of Armory
        for rp in wrd.arm_rplist: # TODO: deprecated
            if rp.rp_gi != 'Off':
                rp.rp_gi = 'Off'
                rp.rp_voxelao = True

        # Replace deprecated nodes
        arm.logicnode.replacement.replace_all()

        wrd.arm_version = props.arm_version
        wrd.arm_commit = props.arm_commit

        arm.make.clean()
        print(f'Project updated to SDK {props.arm_version}. Please save the .blend file.')

        return {'FINISHED'}

class ARM_OT_DiscardPopup(bpy.types.Operator):
    """Empty operator for discarding dialogs."""
    bl_idname = 'arm.discard_popup'
    bl_label = 'OK'
    bl_description = 'Discard'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

class ArmoryUpdateListAndroidEmulatorButton(bpy.types.Operator):
    '''Updating the list of emulators for the Android platform'''
    bl_idname = 'arm.update_list_android_emulator'
    bl_label = 'Update List Emulators'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if len(arm.utils.get_android_sdk_root_path()) == 0:
            return {"CANCELLED"}

        os.environ['ANDROID_SDK_ROOT'] = arm.utils.get_android_sdk_root_path()
        items, err = arm.utils.get_android_emulators_list()
        if len(err) > 0:
            print('Update List Emulators Warning: File "'+ arm.utils.get_android_emulator_file() +'" not found. Check that the variable ANDROID_SDK_ROOT is correct in environment variables or in "Android SDK Path" setting: \n- If you specify an environment variable ANDROID_SDK_ROOT, then you need to restart Blender;\n- If you specify the setting "Android SDK Path", then repeat operation "Publish"')
            return{'FINISHED'}
        if len(items) > 0:
            items_enum = []
            for i in items:
                items_enum.append((i, i, i))
            bpy.types.World.arm_project_android_list_avd = EnumProperty(items=items_enum, name="Emulator", update=assets.invalidate_compiler_cache)
        return{'FINISHED'}

class ArmoryUpdateListAndroidEmulatorRunButton(bpy.types.Operator):
    '''Launch Android emulator selected from the list'''
    bl_idname = 'arm.run_android_emulator'
    bl_label = 'Launch Emulator'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if len(arm.utils.get_android_sdk_root_path()) == 0:
            return {"CANCELLED"}

        make.run_android_emulators(arm.utils.get_android_emulator_name())
        return{'FINISHED'}


class ArmoryUpdateListInstalledVSButton(bpy.types.Operator):
    """Update the list of installed Visual Studio versions for the Windows platform"""
    bl_idname = 'arm.update_list_installed_vs'
    bl_label = '(Re-)Fetch Installed Visual Studio Versions'

    def execute(self, context):
        if not arm.utils.get_os_is_windows():
            return {"CANCELLED"}

        success = arm.utils_vs.fetch_installed_vs()
        if not success:
            self.report({"ERROR"}, "Could not fetch installed Visual Studio versions, check console for details.")
            return {'CANCELLED'}

        return {'FINISHED'}


class ARM_PT_BulletDebugDrawingPanel(bpy.types.Panel):
    bl_label = "Armory Debug Drawing"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "SCENE_PT_rigid_body_world"

    @classmethod
    def poll(cls, context):
        return context.scene.rigidbody_world is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']

        if wrd.arm_physics_engine != 'Bullet':
            row = layout.row()
            row.alert = True
            row.label(text="Physics debug drawing is only supported for the Bullet physics engine")

        col = layout.column(align=False)
        col.prop(wrd, "arm_bullet_dbg_draw_wireframe")
        col.prop(wrd, "arm_bullet_dbg_draw_aabb")
        col.prop(wrd, "arm_bullet_dbg_draw_contact_points")
        col.prop(wrd, "arm_bullet_dbg_draw_constraints")
        col.prop(wrd, "arm_bullet_dbg_draw_constraint_limits")
        col.prop(wrd, "arm_bullet_dbg_draw_normals")
        col.prop(wrd, "arm_bullet_dbg_draw_axis_gizmo")

def draw_custom_node_menu(self, context):
    """Extension of the node context menu.

    https://blender.stackexchange.com/questions/150101/python-how-to-add-items-in-context-menu-in-2-8
    """
    if context.selected_nodes is None or len(context.selected_nodes) != 1:
        return

    if context.space_data.tree_type == 'ArmLogicTreeType':
        if context.selected_nodes[0].bl_idname.startswith('LN'):
            layout = self.layout
            layout.separator()
            layout.operator("arm.open_node_documentation", text="Show documentation for this node", icon='HELP')
            layout.operator("arm.open_node_haxe_source", text="Open .hx source in the browser", icon_value=ui_icons.get_id("haxe"))
            layout.operator("arm.open_node_python_source", text="Open .py source in the browser", icon='FILE_SCRIPT')

    elif context.space_data.tree_type == 'ShaderNodeTree':
        if context.active_node.bl_idname in ('ShaderNodeRGB', 'ShaderNodeValue', 'ShaderNodeTexImage'):
            layout = self.layout
            layout.separator()
            layout.prop(context.active_node, 'arm_material_param', text='Armory: Material Parameter')

def draw_conditional_prop(layout: bpy.types.UILayout, heading: str, data: bpy.types.AnyType, prop_condition: str, prop_value: str) -> None:
    """Draws a property row with a checkbox that enables a value field.
    The function fails when prop_condition is not a boolean property.
    """
    col = layout.column(heading=heading)
    row = col.row()
    row.prop(data, prop_condition, text='')
    sub = row.row()
    sub.enabled = getattr(data, prop_condition)
    sub.prop(data, prop_value, expand=True)


def draw_error_box(layout: bpy.types.UILayout, text: str) -> bpy.types.UILayout:
    """Draw an error box in the given UILayout and return it for
    further optional modification. The text is wrapped automatically
    according to the current region's width.
    """
    textwrap_width = max(0, int((bpy.context.region.width - 25) / 6))
    lines = textwrap.wrap(text, width=textwrap_width, break_long_words=True)

    box = layout.box()
    col = box.column(align=True)
    col.alert = True
    for idx, line in enumerate(lines):
        col.label(text=line, icon='ERROR' if idx == 0 else 'BLANK1')

    return box


def draw_multiline_with_icon(layout: bpy.types.UILayout, layout_width_px: int, icon: str, text: str) -> bpy.types.UILayout:
    """Draw a multiline string with an icon in the given UILayout
    and return it for further optional modification.
    The text is wrapped according to the given layout width.
    """
    textwrap_width = max(0, layout_width_px // 6)
    lines = textwrap.wrap(text, width=textwrap_width, break_long_words=True)

    col = layout.column(align=True)
    col.scale_y = 0.8
    for idx, line in enumerate(lines):
        col.label(text=line, icon=icon if idx == 0 else 'BLANK1')

    return col


__REG_CLASSES = (
    ARM_PT_ObjectPropsPanel,
    ARM_PT_ModifiersPropsPanel,
    ARM_PT_ParticlesPropsPanel,
    ARM_PT_PhysicsPropsPanel,
    ARM_PT_DataPropsPanel,
    ARM_PT_ScenePropsPanel,
    ARM_PT_WorldPropsPanel,
    InvalidateCacheButton,
    InvalidateMaterialCacheButton,
    ARM_OT_NewCustomMaterial,
    ARM_PG_BindTexturesListItem,
    ARM_UL_BindTexturesList,
    ARM_OT_BindTexturesListNewItem,
    ARM_OT_BindTexturesListDeleteItem,
    ARM_PT_MaterialPropsPanel,
    ARM_PT_BindTexturesPropsPanel,
    ARM_PT_MaterialBlendingPropsPanel,
    ARM_PT_MaterialDriverPropsPanel,
    ARM_PT_ArmoryPlayerPanel,
    ARM_PT_TopbarPanel,
    ARM_PT_ArmoryExporterPanel,
    ARM_PT_ArmoryExporterAndroidSettingsPanel,
    ARM_PT_ArmoryExporterAndroidPermissionsPanel,
    ARM_PT_ArmoryExporterAndroidAbiPanel,
    ARM_PT_ArmoryExporterAndroidBuildAPKPanel,
    ARM_PT_ArmoryExporterHTML5SettingsPanel,
    ARM_PT_ArmoryExporterWindowsSettingsPanel,
    ARM_PT_ArmoryProjectPanel,
    ARM_PT_ProjectFlagsPanel,
    ARM_PT_ProjectFlagsDebugConsolePanel,
    ARM_PT_ProjectWindowPanel,
    ARM_PT_ProjectModulesPanel,
    ARM_PT_RenderPathPanel,
    ARM_PT_RenderPathRendererPanel,
    ARM_PT_RenderPathShadowsPanel,
    ARM_PT_RenderPathVoxelsPanel,
    ARM_PT_RenderPathWorldPanel,
    ARM_PT_RenderPathPostProcessPanel,
    ARM_PT_RenderPathCompositorPanel,
    ARM_PT_BakePanel,
    # ArmVirtualInputPanel,
    ArmoryPlayButton,
    ArmoryStopButton,
    ArmoryBuildProjectButton,
    ArmoryOpenProjectFolderButton,
    ArmoryOpenEditorButton,
    CleanMenu,
    CleanButtonMenu,
    ArmoryCleanProjectButton,
    ArmoryPublishProjectButton,
    ArmGenLodButton,
    ARM_PT_LodPanel,
    ArmGenTerrainButton,
    ARM_PT_TerrainPanel,
    ARM_PT_TilesheetPanel,
    ArmPrintTraitsButton,
    ARM_PT_MaterialNodePanel,
    ARM_OT_UpdateFileSDK,
    ARM_OT_CopyToBundled,
    ARM_OT_ShowFileVersionInfo,
    ARM_OT_ShowNodeUpdateErrors,
    ARM_OT_DiscardPopup,
    ArmoryUpdateListAndroidEmulatorButton,
    ArmoryUpdateListAndroidEmulatorRunButton,
    ArmoryUpdateListInstalledVSButton,
    ARM_PT_BulletDebugDrawingPanel,
    ARM_OT_AddArmatureRootMotion,
    scene.TLM_PT_Settings,
    scene.TLM_PT_Denoise,
    scene.TLM_PT_Filtering,
    scene.TLM_PT_Encoding,
    scene.TLM_PT_Utility,
    scene.TLM_PT_Additional,
)
__reg_classes, __unreg_classes = bpy.utils.register_classes_factory(__REG_CLASSES)


def register():
    __reg_classes()

    bpy.types.VIEW3D_HT_header.append(draw_view3d_header)
    bpy.types.VIEW3D_MT_object.append(draw_view3d_object_menu)
    bpy.types.NODE_MT_context_menu.append(draw_custom_node_menu)
    bpy.types.TOPBAR_HT_upper_bar.prepend(draw_space_topbar)

    bpy.types.Material.arm_bind_textures_list = CollectionProperty(type=ARM_PG_BindTexturesListItem)
    bpy.types.Material.arm_bind_textures_list_index = IntProperty(name='Index for arm_bind_textures_list', default=0)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(draw_custom_node_menu)
    bpy.types.VIEW3D_MT_object.remove(draw_view3d_object_menu)
    bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)
    bpy.types.TOPBAR_HT_upper_bar.remove(draw_space_topbar)

    __unreg_classes()
