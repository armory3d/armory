import os
import time

import bpy
from bpy.props import *

import arm.api
import arm.assets as assets
import arm.log as log
import arm.make as make
import arm.make_state as state
import arm.props as props
import arm.props_properties
import arm.nodes_logic
import arm.proxy
import arm.utils

from arm.lightmapper.utility import icon
from arm.lightmapper.properties.denoiser import oidn, optix
import importlib

# Menu in object region
class ARM_PT_ObjectPropsPanel(bpy.types.Panel):
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

        layout.prop(obj, 'arm_export')
        if not obj.arm_export:
            return
        layout.prop(obj, 'arm_spawn')
        layout.prop(obj, 'arm_mobile')
        layout.prop(obj, 'arm_animation_enabled')

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

        # Properties list
        arm.props_properties.draw_properties(layout, obj)

        # Lightmapping props
        if obj.type == "MESH":
            row = layout.row(align=True)
            scene = bpy.context.scene
            if scene == None:
                return
            row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_use")

            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_resolution")
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

        if obj.rigid_body != None:
            layout.prop(obj, 'arm_rb_linear_factor')
            layout.prop(obj, 'arm_rb_angular_factor')
            layout.prop(obj, 'arm_rb_trigger')
            layout.prop(obj, 'arm_rb_ccd')

        if obj.soft_body != None:
            layout.prop(obj, 'arm_soft_body_margin')

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
    '''Delete cached mesh data'''
    bl_idname = "arm.invalidate_cache"
    bl_label = "Invalidate Cache"

    def execute(self, context):
        context.object.data.arm_cached = False
        return{'FINISHED'}

class InvalidateMaterialCacheButton(bpy.types.Operator):
    '''Delete cached material data'''
    bl_idname = "arm.invalidate_material_cache"
    bl_label = "Invalidate Cache"

    def execute(self, context):
        context.material.arm_cached = False
        context.material.signature = ''
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
        layout.prop(mat, 'arm_two_sided')
        columnb = layout.column()
        columnb.enabled = not mat.arm_two_sided
        columnb.prop(mat, 'arm_cull_mode')
        layout.prop(mat, 'arm_material_id')
        layout.prop(mat, 'arm_overlay')
        layout.prop(mat, 'arm_decal')
        layout.prop(mat, 'arm_discard')
        columnb = layout.column()
        columnb.enabled = mat.arm_discard
        columnb.prop(mat, 'arm_discard_opacity')
        columnb.prop(mat, 'arm_discard_opacity_shadows')
        layout.prop(mat, 'arm_custom_material')
        layout.prop(mat, 'arm_skip_context')
        layout.prop(mat, 'arm_particle_fade')
        layout.prop(mat, 'arm_billboard')

        layout.operator("arm.invalidate_material_cache")


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
        if context.material == None:
            return
        self.layout.prop(context.material, 'arm_blending', text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        mat = bpy.context.material
        if mat == None:
            return

        flow = layout.grid_flow()
        flow.enabled = mat.arm_blending
        col = flow.column()
        col.prop(mat, 'arm_blending_source')
        col.prop(mat, 'arm_blending_destination')
        col.prop(mat, 'arm_blending_operation')
        col = flow.column()
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
        if state.proc_play is None and state.proc_build is None:
            row.operator("arm.play", icon="PLAY")
        else:
            row.operator("arm.stop", icon="MESH_PLANE")
        row.operator("arm.clean_menu")
        layout.prop(wrd, 'arm_runtime')
        layout.prop(wrd, 'arm_play_camera')
        layout.prop(wrd, 'arm_play_scene')

        if log.num_warnings > 0:
            box = layout.box()
            # Less spacing between lines
            col = box.column(align=True)
            col.label(text=f'{log.num_warnings} warnings occurred during compilation!', icon='ERROR')
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
        row.operator("arm.build_project")
        # row.operator("arm.patch_project")
        row.operator("arm.publish_project", icon="EXPORT")
        row.enabled = wrd.arm_exporterlist_index >= 0 and len(wrd.arm_exporterlist) > 0

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
            if item.arm_project_target == 'custom':
                box.prop(item, 'arm_project_khamake')
            box.prop(item, arm.utils.target_to_gapi(item.arm_project_target))
            wrd.arm_rpcache_list.clear() # Make UIList work with prop_search()
            for i in wrd.arm_rplist:
                wrd.arm_rpcache_list.add().name = i.name
            box.prop_search(item, "arm_project_rp", wrd, "arm_rpcache_list", text="Render Path")
            box.prop_search(item, 'arm_project_scene', bpy.data, 'scenes', text='Scene')
            layout.separator()

        col = layout.column()
        col.prop(wrd, 'arm_project_name')
        col.prop(wrd, 'arm_project_package')
        col.prop(wrd, 'arm_project_bundle')
        col.prop(wrd, 'arm_project_version')
        col.prop(wrd, 'arm_project_version_autoinc')
        col.prop(wrd, 'arm_project_icon')
        col.prop(wrd, 'arm_dce')
        col.prop(wrd, 'arm_compiler_inline')
        col.prop(wrd, 'arm_minify_js')
        col.prop(wrd, 'arm_optimize_data')
        col.prop(wrd, 'arm_asset_compression')
        col.prop(wrd, 'arm_single_data_file')

class ARM_PT_ArmoryExporterAndroidSettingsPanel(bpy.types.Panel):
    bl_label = "Android Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = { 'HIDE_HEADER' }
    bl_parent_id = "ARM_PT_ArmoryExporterPanel"

    @classmethod
    def poll(cls, context):
        wrd = bpy.data.worlds['Arm']
        if (len(wrd.arm_exporterlist) > 0) and (wrd.arm_exporterlist_index >= 0):
            item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
            return item.arm_project_target == 'android-hl'
        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        # Options
        layout.label(text='Android Settings', icon='SETTINGS')
        row = layout.row()
        row.prop(wrd, 'arm_winorient')
        row = layout.row()
        row.prop(wrd, 'arm_project_android_sdk_compile')
        row = layout.row()
        row.prop(wrd, 'arm_project_android_sdk_min')
        row = layout.row()
        row.prop(wrd, 'arm_project_android_sdk_target')

class ARM_PT_ArmoryExporterAndroidPermissionsPanel(bpy.types.Panel):
    bl_label = "Permissions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = { 'DEFAULT_CLOSED' }
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
    bl_options = { 'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ArmoryExporterAndroidSettingsPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        row = layout.row()
        row.prop(wrd, 'arm_project_android_build_apk')
        path = arm.utils.get_android_sdk_root_path()
        row.enabled = len(path) > 0
        row = layout.row()
        row.prop(wrd, 'arm_project_android_rename_apk')
        row.enabled = wrd.arm_project_android_build_apk
        row = layout.row()
        row.prop(wrd, 'arm_project_android_copy_apk')
        row.enabled = (wrd.arm_project_android_build_apk) and (len(arm.utils.get_android_apk_copy_path()) > 0)
        row = layout.row()
        row.prop(wrd, 'arm_project_android_list_avd')
        col = row.column(align=True)
        col.operator('arm.update_list_android_emulator', text='', icon='FILE_REFRESH')
        col.enabled = len(path) > 0
        col = row.column(align=True)
        col.operator('arm.run_android_emulator', text='', icon='PLAY')
        col.enabled = len(path) > 0 and len(arm.utils.get_android_emulator_name()) > 0
        row = layout.row()
        row.prop(wrd, 'arm_project_android_run_avd')
        row.enabled = arm.utils.get_project_android_build_apk() and len(arm.utils.get_android_emulator_name()) > 0

class ARM_PT_ArmoryExporterHTML5SettingsPanel(bpy.types.Panel):
    bl_label = "HTML5 Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = { 'HIDE_HEADER' }
    bl_parent_id = "ARM_PT_ArmoryExporterPanel"

    @classmethod
    def poll(cls, context):
        wrd = bpy.data.worlds['Arm']
        if (len(wrd.arm_exporterlist) > 0) and (wrd.arm_exporterlist_index >= 0):
            item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
            return item.arm_project_target == 'html5'
        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        # Options
        layout.label(text='HTML5 Settings', icon='SETTINGS')
        row = layout.row()
        row.prop(wrd, 'arm_project_html5_copy')
        row.enabled = len(arm.utils.get_html5_copy_path()) > 0
        row = layout.row()
        row.prop(wrd, 'arm_project_html5_start_browser')
        row.enabled = (len(arm.utils.get_html5_copy_path()) > 0) and (wrd.arm_project_html5_copy) and (len(arm.utils.get_link_web_server()) > 0)

class ARM_PT_ArmoryExporterWindowsSettingsPanel(bpy.types.Panel):
    bl_label = "Windows Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = { 'HIDE_HEADER' }
    bl_parent_id = "ARM_PT_ArmoryExporterPanel"

    @classmethod
    def poll(cls, context):
        wrd = bpy.data.worlds['Arm']
        if (len(wrd.arm_exporterlist) > 0) and (wrd.arm_exporterlist_index >= 0):
            item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
            return item.arm_project_target == 'windows-hl'
        else:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        # Options
        layout.label(text='Windows Settings', icon='SETTINGS')
        row = layout.row()
        row.prop(wrd, 'arm_project_win_list_vs')
        col = row.column(align=True)
        col.operator('arm.update_list_installed_vs', text='', icon='FILE_REFRESH')
        col.enabled = arm.utils.get_os_is_windows()
        row = layout.row()
        row.prop(wrd, 'arm_project_win_build')
        row.enabled = arm.utils.get_os_is_windows()
        is_enable = arm.utils.get_os_is_windows() and wrd.arm_project_win_build != '0' and wrd.arm_project_win_build != '1'
        row = layout.row()
        row.prop(wrd, 'arm_project_win_build_mode')
        row.enabled = is_enable
        row = layout.row()
        row.prop(wrd, 'arm_project_win_build_arch')
        row.enabled = is_enable
        row = layout.row()
        row.prop(wrd, 'arm_project_win_build_log')
        row.enabled = is_enable
        row = layout.row()
        row.prop(wrd, 'arm_project_win_build_cpu')
        row.enabled = is_enable
        row = layout.row()
        row.prop(wrd, 'arm_project_win_build_open')
        row.enabled = is_enable

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
        layout.prop(wrd, 'arm_verbose_output')
        layout.prop(wrd, 'arm_cache_build')
        layout.prop(wrd, 'arm_live_patch')
        layout.prop(wrd, 'arm_stream_scene')
        layout.prop(wrd, 'arm_batch_meshes')
        layout.prop(wrd, 'arm_batch_materials')
        layout.prop(wrd, 'arm_write_config')
        layout.prop(wrd, 'arm_minimize')
        layout.prop(wrd, 'arm_deinterleaved_buffers')
        layout.prop(wrd, 'arm_export_tangents')
        layout.prop(wrd, 'arm_loadscreen')
        layout.prop(wrd, 'arm_texture_quality')
        layout.prop(wrd, 'arm_sound_quality')

class ARM_PT_ProjectFlagsDebugConsolePanel(bpy.types.Panel):
    bl_label = "Debug Console"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_ProjectFlagsPanel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        row = layout.row()
        row.enabled = wrd.arm_ui != 'Disabled'
        row.prop(wrd, 'arm_debug_console')
        row = layout.row()
        row.enabled = wrd.arm_debug_console
        row.prop(wrd, 'arm_debug_console_position')
        row = layout.row()
        row.enabled = wrd.arm_debug_console
        row.prop(wrd, 'arm_debug_console_scale')
        row = layout.row()
        row.enabled = wrd.arm_debug_console
        row.prop(wrd, 'arm_debug_console_visible')

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
        layout.prop(wrd, 'arm_winresize')
        col = layout.column()
        col.enabled = wrd.arm_winresize
        col.prop(wrd, 'arm_winmaximize')
        layout.prop(wrd, 'arm_winminimize')
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
        layout.prop_search(wrd, 'arm_khafile', bpy.data, 'texts', text='Khafile')
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

    def execute(self, context):
        if state.proc_build != None:
            return {"CANCELLED"}

        # Compare version Blender and Armory (major, minor)
        if not arm.utils.compare_version_blender_arm():
            self.report({'INFO'}, 'For Armory to work correctly, you need Blender 2.83 LTS.')

        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        arm.utils.check_projectpath(None)

        arm.utils.check_default_props()

        assets.invalidate_enabled = False
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
        return{'FINISHED'}

class ArmoryBuildProjectButton(bpy.types.Operator):
    '''Build and compile project'''
    bl_idname = 'arm.build_project'
    bl_label = 'Build'

    def execute(self, context):
        # Compare version Blender and Armory (major, minor)
        if not arm.utils.compare_version_blender_arm():
            self.report({'INFO'}, 'For Armory to work correctly, you need Blender 2.83 LTS.')

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
        make.build(item.arm_project_target, is_export=True)
        make.compile()
        wrd.arm_rplist_index = rplist_index
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryPublishProjectButton(bpy.types.Operator):
    '''Build project ready for publishing'''
    bl_idname = 'arm.publish_project'
    bl_label = 'Publish'

    def execute(self, context):
        # Compare version Blender and Armory (major, minor)
        if not arm.utils.compare_version_blender_arm():
            self.report({'INFO'}, 'For Armory to work correctly, you need Blender 2.83 LTS.')

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
            rpdat.rp_driver_list.clear()
            rpdat.rp_driver_list.add().name = 'Armory'
            for d in arm.api.drivers:
                rpdat.rp_driver_list.add().name = arm.api.drivers[d]['driver_name']
            layout.prop_search(rpdat, "rp_driver", rpdat, "rp_driver_list", text="Driver")
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
        layout.prop(rpdat, 'arm_skin')
        row = layout.row()
        row.enabled = rpdat.arm_skin == 'On'
        row.prop(rpdat, 'arm_skin_max_bones_auto')
        row = layout.row()
        row.enabled = not rpdat.arm_skin_max_bones_auto
        row.prop(rpdat, 'arm_skin_max_bones')
        layout.prop(rpdat, "rp_hdr")
        layout.prop(rpdat, "rp_stereo")
        layout.prop(rpdat, 'arm_culling')
        layout.prop(rpdat, 'rp_pp')

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

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.enabled = rpdat.rp_shadows
        layout.prop(rpdat, 'rp_shadowmap_cube')
        layout.prop(rpdat, 'rp_shadowmap_cascade')
        layout.prop(rpdat, 'rp_shadowmap_cascades')
        col = layout.column()
        col2 = col.column()
        col2.enabled = rpdat.rp_shadowmap_cascades != '1'
        col2.prop(rpdat, 'arm_shadowmap_split')
        col.prop(rpdat, 'arm_shadowmap_bounds')
        col.prop(rpdat, 'arm_pcfsize')

class ARM_PT_RenderPathVoxelsPanel(bpy.types.Panel):
    bl_label = "Voxel AO"
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
        self.layout.prop(rpdat, "rp_voxelao", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_rplist) <= wrd.arm_rplist_index:
            return
        rpdat = wrd.arm_rplist[wrd.arm_rplist_index]

        layout.enabled = rpdat.rp_voxelao
        layout.prop(rpdat, 'arm_voxelgi_shadows')
        layout.prop(rpdat, 'arm_voxelgi_cones')
        layout.prop(rpdat, 'rp_voxelgi_resolution')
        layout.prop(rpdat, 'rp_voxelgi_resolution_z')
        layout.prop(rpdat, 'arm_voxelgi_dimensions')
        layout.prop(rpdat, 'arm_voxelgi_revoxelize')
        col2 = layout.column()
        col2.enabled = rpdat.arm_voxelgi_revoxelize
        col2.prop(rpdat, 'arm_voxelgi_camera')
        col2.prop(rpdat, 'arm_voxelgi_temporal')
        layout.prop(rpdat, 'arm_voxelgi_occ')
        layout.prop(rpdat, 'arm_voxelgi_step')
        layout.prop(rpdat, 'arm_voxelgi_range')
        layout.prop(rpdat, 'arm_voxelgi_offset')
        layout.prop(rpdat, 'arm_voxelgi_aperture')

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
        layout.prop(rpdat, 'arm_irradiance')
        col = layout.column()
        col.enabled = rpdat.arm_irradiance
        col.prop(rpdat, 'arm_radiance')
        colb = col.column()
        colb.enabled = rpdat.arm_radiance
        colb.prop(rpdat, 'arm_radiance_size')
        layout.prop(rpdat, 'arm_clouds')
        layout.prop(rpdat, "rp_water")
        col = layout.column(align=True)
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
        row = layout.row()
        row.prop(rpdat, "rp_antialiasing")
        layout.prop(rpdat, "rp_supersampling")
        layout.prop(rpdat, 'arm_rp_resolution')
        if rpdat.arm_rp_resolution == 'Custom':
            layout.prop(rpdat, 'arm_rp_resolution_size')
            layout.prop(rpdat, 'arm_rp_resolution_filter')
        layout.prop(rpdat, 'rp_dynres')
        layout.separator()
        row = layout.row()
        row.prop(rpdat, "rp_ssgi")
        col = layout.column()
        col.enabled = rpdat.rp_ssgi != 'Off'
        col.prop(rpdat, 'arm_ssgi_half_res')
        col.prop(rpdat, 'arm_ssgi_rays')
        col.prop(rpdat, 'arm_ssgi_radius')
        col.prop(rpdat, 'arm_ssgi_strength')
        col.prop(rpdat, 'arm_ssgi_max_steps')
        layout.separator()
        layout.prop(rpdat, "rp_ssr")
        col = layout.column()
        col.enabled = rpdat.rp_ssr
        col.prop(rpdat, 'arm_ssr_half_res')
        col.prop(rpdat, 'arm_ssr_ray_step')
        col.prop(rpdat, 'arm_ssr_min_ray_step')
        col.prop(rpdat, 'arm_ssr_search_dist')
        col.prop(rpdat, 'arm_ssr_falloff_exp')
        col.prop(rpdat, 'arm_ssr_jitter')
        layout.separator()
        layout.prop(rpdat, 'arm_ssrs')
        col = layout.column()
        col.enabled = rpdat.arm_ssrs
        col.prop(rpdat, 'arm_ssrs_ray_step')
        layout.prop(rpdat, 'arm_micro_shadowing')
        layout.separator()
        layout.prop(rpdat, "rp_bloom")
        col = layout.column()
        col.enabled = rpdat.rp_bloom
        col.prop(rpdat, 'arm_bloom_threshold')
        col.prop(rpdat, 'arm_bloom_strength')
        col.prop(rpdat, 'arm_bloom_radius')
        layout.separator()
        layout.prop(rpdat, "rp_motionblur")
        col = layout.column()
        col.enabled = rpdat.rp_motionblur != 'Off'
        col.prop(rpdat, 'arm_motion_blur_intensity')
        layout.separator()
        layout.prop(rpdat, "rp_volumetriclight")
        col = layout.column()
        col.enabled = rpdat.rp_volumetriclight
        col.prop(rpdat, 'arm_volumetric_light_air_color')
        col.prop(rpdat, 'arm_volumetric_light_air_turbidity')
        col.prop(rpdat, 'arm_volumetric_light_steps')
        layout.separator()
        layout.prop(rpdat, "rp_chromatic_aberration")
        col = layout.column()
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
        layout.prop(rpdat, 'arm_letterbox')
        col = layout.column()
        col.enabled = rpdat.arm_letterbox
        col.prop(rpdat, 'arm_letterbox_size')
        layout.prop(rpdat, 'arm_sharpen')
        col = layout.column()
        col.enabled = rpdat.arm_sharpen
        col.prop(rpdat, 'arm_sharpen_strength')
        layout.prop(rpdat, 'arm_fisheye')
        layout.prop(rpdat, 'arm_vignette')
        col = layout.column()
        col.enabled = rpdat.arm_vignette
        col.prop(rpdat, 'arm_vignette_strength')
        layout.prop(rpdat, 'arm_lensflare')
        layout.prop(rpdat, 'arm_grain')
        col = layout.column()
        col.enabled = rpdat.arm_grain
        col.prop(rpdat, 'arm_grain_strength')
        layout.prop(rpdat, 'arm_fog')
        col = layout.column(align=True)
        col.enabled = rpdat.arm_fog
        col.prop(rpdat, 'arm_fog_color')
        col.prop(rpdat, 'arm_fog_amounta')
        col.prop(rpdat, 'arm_fog_amountb')
        layout.separator()
        layout.prop(rpdat, "rp_autoexposure")
        col = layout.column()
        col.enabled = rpdat.rp_autoexposure
        col.prop(rpdat, 'arm_autoexposure_strength', text='Strength')
        col.prop(rpdat, 'arm_autoexposure_speed', text='Speed')
        layout.prop(rpdat, 'arm_lens_texture')
        if rpdat.arm_lens_texture != "":
            layout.prop(rpdat, 'arm_lens_texture_masking')
            if rpdat.arm_lens_texture_masking:
                layout.prop(rpdat, 'arm_lens_texture_masking_centerMinClip')
                layout.prop(rpdat, 'arm_lens_texture_masking_centerMaxClip')
                layout.prop(rpdat, 'arm_lens_texture_masking_luminanceMin')
                layout.prop(rpdat, 'arm_lens_texture_masking_luminanceMax')
                layout.prop(rpdat, 'arm_lens_texture_masking_brightnessExp')
        layout.prop(rpdat, 'arm_lut_texture')

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

        else:

            scene = context.scene
            sceneProperties = scene.TLM_SceneProperties
            row = layout.row(align=True)

            row = layout.row(align=True)

            #We list LuxCoreRender as available, by default we assume Cycles exists
            row.prop(sceneProperties, "tlm_lightmap_engine")

            if sceneProperties.tlm_lightmap_engine == "Cycles":

                #CYCLES SETTINGS HERE
                engineProperties = scene.TLM_EngineProperties

                row = layout.row(align=True)
                row.label(text="General Settings")
                row = layout.row(align=True)
                row.operator("tlm.build_lightmaps")
                row = layout.row(align=True)
                row.operator("tlm.clean_lightmaps")
                row = layout.row(align=True)
                row.operator("tlm.explore_lightmaps")
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_apply_on_unwrap")
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_headless")
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_alert_on_finish")

                if sceneProperties.tlm_alert_on_finish:
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_alert_sound")

                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_verbose")
                #row = layout.row(align=True)
                #row.prop(sceneProperties, "tlm_compile_statistics")
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_override_bg_color")
                if sceneProperties.tlm_override_bg_color:
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_override_color")
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_reset_uv")

                row = layout.row(align=True)
                try:
                    if bpy.context.scene["TLM_Buildstat"] is not None:
                        row.label(text="Last build completed in: " + str(bpy.context.scene["TLM_Buildstat"][0]))
                except:
                    pass

                row = layout.row(align=True)
                row.label(text="Cycles Settings")

                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_mode")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_quality")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_resolution_scale")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_bake_mode")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_lighting_mode")

                if scene.TLM_EngineProperties.tlm_bake_mode == "Background":
                    row = layout.row(align=True)
                    row.label(text="Warning! Background mode is currently unstable", icon_value=2)
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_network_render")
                    if sceneProperties.tlm_network_render:
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_network_paths")
                        #row = layout.row(align=True)
                        #row.prop(sceneProperties, "tlm_network_dir")
                row = layout.row(align=True)
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_caching_mode")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_directional_mode")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_lightmap_savedir")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_dilation_margin")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_exposure_multiplier")
                row = layout.row(align=True)
                row.prop(engineProperties, "tlm_setting_supersample")
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_metallic_clamp")

            elif sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

                #LUXCORE SETTINGS HERE
                luxcore_available = False

                #Look for Luxcorerender in the renderengine classes
                for engine in bpy.types.RenderEngine.__subclasses__():
                    if engine.bl_idname == "LUXCORE":
                        luxcore_available = True
                        break

                row = layout.row(align=True)
                if not luxcore_available:
                    row.label(text="Please install BlendLuxCore.")
                else:
                    row.label(text="LuxCoreRender not yet available.")

            elif sceneProperties.tlm_lightmap_engine == "OctaneRender":

                #LUXCORE SETTINGS HERE
                octane_available = False

                row = layout.row(align=True)
                row.label(text="Octane Render not yet available.")


            ##################
            #DENOISE SETTINGS!
            row = layout.row(align=True)
            row.label(text="Denoise Settings")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_denoise_use")
            row = layout.row(align=True)

            if sceneProperties.tlm_denoise_use:
                row.prop(sceneProperties, "tlm_denoise_engine", expand=True)
                row = layout.row(align=True)

                if sceneProperties.tlm_denoise_engine == "Integrated":
                    row.label(text="No options for Integrated.")
                elif sceneProperties.tlm_denoise_engine == "OIDN":
                    denoiseProperties = scene.TLM_OIDNEngineProperties
                    row.prop(denoiseProperties, "tlm_oidn_path")
                    row = layout.row(align=True)
                    row.prop(denoiseProperties, "tlm_oidn_verbose")
                    row = layout.row(align=True)
                    row.prop(denoiseProperties, "tlm_oidn_threads")
                    row = layout.row(align=True)
                    row.prop(denoiseProperties, "tlm_oidn_maxmem")
                    row = layout.row(align=True)
                    row.prop(denoiseProperties, "tlm_oidn_affinity")
                    # row = layout.row(align=True)
                    # row.prop(denoiseProperties, "tlm_denoise_ao")
                elif sceneProperties.tlm_denoise_engine == "Optix":
                    denoiseProperties = scene.TLM_OptixEngineProperties
                    row.prop(denoiseProperties, "tlm_optix_path")
                    row = layout.row(align=True)
                    row.prop(denoiseProperties, "tlm_optix_verbose")
                    row = layout.row(align=True)
                    row.prop(denoiseProperties, "tlm_optix_maxmem")


            ##################
            #FILTERING SETTINGS!
            row = layout.row(align=True)
            row.label(text="Filtering Settings")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_filtering_use")
            row = layout.row(align=True)

            if sceneProperties.tlm_filtering_use:

                if sceneProperties.tlm_filtering_engine == "OpenCV":

                    cv2 = importlib.util.find_spec("cv2")

                    if cv2 is None:
                        row = layout.row(align=True)
                        row.label(text="OpenCV is not installed. Install it below.")
                        row = layout.row(align=True)
                        row.label(text="It is recommended to install as administrator.")
                        row = layout.row(align=True)
                        row.operator("tlm.install_opencv_lightmaps")
                    else:
                        row = layout.row(align=True)
                        row.prop(scene.TLM_SceneProperties, "tlm_filtering_mode")
                        row = layout.row(align=True)
                        if scene.TLM_SceneProperties.tlm_filtering_mode == "Gaussian":
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_gaussian_strength")
                            row = layout.row(align=True)
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")
                        elif scene.TLM_SceneProperties.tlm_filtering_mode == "Box":
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_box_strength")
                            row = layout.row(align=True)
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")

                        elif scene.TLM_SceneProperties.tlm_filtering_mode == "Bilateral":
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_bilateral_diameter")
                            row = layout.row(align=True)
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_bilateral_color_deviation")
                            row = layout.row(align=True)
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_bilateral_coordinate_deviation")
                            row = layout.row(align=True)
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")
                        else:
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_median_kernel", expand=True)
                            row = layout.row(align=True)
                            row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")
                else:
                    row = layout.row(align=True)
                    row.prop(scene.TLM_SceneProperties, "tlm_numpy_filtering_mode")


            ##################
            #ENCODING SETTINGS!
            row = layout.row(align=True)
            row.label(text="Encoding Settings")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_encoding_use")
            row = layout.row(align=True)

            if sceneProperties.tlm_encoding_use:


                if scene.TLM_EngineProperties.tlm_bake_mode == "Background":
                    row.label(text="Encoding options disabled in background mode")
                    row = layout.row(align=True)

                row.prop(sceneProperties, "tlm_encoding_device", expand=True)
                row = layout.row(align=True)

                if sceneProperties.tlm_encoding_device == "CPU":
                    row.prop(sceneProperties, "tlm_encoding_mode_a", expand=True)
                else:
                    row.prop(sceneProperties, "tlm_encoding_mode_b", expand=True)

                if sceneProperties.tlm_encoding_device == "CPU":
                    if sceneProperties.tlm_encoding_mode_a == "RGBM":
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_encoding_range")
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_decoder_setup")
                    if sceneProperties.tlm_encoding_mode_a == "RGBD":
                        pass
                    if sceneProperties.tlm_encoding_mode_a == "HDR":
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_format")
                else:

                    if sceneProperties.tlm_encoding_mode_b == "RGBM":
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_encoding_range")
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_decoder_setup")

                    if sceneProperties.tlm_encoding_mode_b == "LogLuv" and sceneProperties.tlm_encoding_device == "GPU":
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_decoder_setup")
                    if sceneProperties.tlm_encoding_mode_b == "HDR":
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_format")

            ##################
            #SELECTION OPERATORS!

            row = layout.row(align=True)
            row.label(text="Selection Operators")
            row = layout.row(align=True)

            row = layout.row(align=True)
            row.operator("tlm.enable_selection")
            row = layout.row(align=True)
            row.operator("tlm.disable_selection")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_override_object_settings")

            if sceneProperties.tlm_override_object_settings:

                row = layout.row(align=True)
                row = layout.row()
                row.prop(sceneProperties, "tlm_mesh_lightmap_unwrap_mode")
                row = layout.row()

                if sceneProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":

                    if scene.TLM_AtlasListItem >= 0 and len(scene.TLM_AtlasList) > 0:
                        row = layout.row()
                        item = scene.TLM_AtlasList[scene.TLM_AtlasListItem]
                        row.prop_search(sceneProperties, "tlm_atlas_pointer", scene, "TLM_AtlasList", text='Atlas Group')
                    else:
                        row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")

                else:
                    row = layout.row()
                    row.prop(sceneProperties, "tlm_postpack_object")
                    row = layout.row()

                if sceneProperties.tlm_postpack_object and sceneProperties.tlm_mesh_lightmap_unwrap_mode != "AtlasGroupA":
                    if scene.TLM_PostAtlasListItem >= 0 and len(scene.TLM_PostAtlasList) > 0:
                        row = layout.row()
                        item = scene.TLM_PostAtlasList[scene.TLM_PostAtlasListItem]
                        row.prop_search(sceneProperties, "tlm_postatlas_pointer", scene, "TLM_PostAtlasList", text='Atlas Group')
                        row = layout.row()

                    else:
                        row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")
                        row = layout.row()

                if sceneProperties.tlm_mesh_lightmap_unwrap_mode != "AtlasGroupA":
                    row.prop(sceneProperties, "tlm_mesh_lightmap_resolution")
                    row = layout.row()
                    row.prop(sceneProperties, "tlm_mesh_unwrap_margin")

            row = layout.row(align=True)
            row.operator("tlm.remove_uv_selection")
            row = layout.row(align=True)
            row.operator("tlm.select_lightmapped_objects")
            row = layout.row(align=True)

            ##################
            #Additional settings
            row = layout.row(align=True)
            row.label(text="Additional options")
            sceneProperties = scene.TLM_SceneProperties
            atlasListItem = scene.TLM_AtlasListItem
            atlasList = scene.TLM_AtlasList
            postatlasListItem = scene.TLM_PostAtlasListItem
            postatlasList = scene.TLM_PostAtlasList

            layout.label(text="Atlas Groups")
            row = layout.row()
            row.prop(sceneProperties, "tlm_atlas_mode", expand=True)

            if sceneProperties.tlm_atlas_mode == "Prepack":

                rows = 2
                if len(atlasList) > 1:
                    rows = 4
                row = layout.row()
                row.template_list("TLM_UL_AtlasList", "Atlas List", scene, "TLM_AtlasList", scene, "TLM_AtlasListItem", rows=rows)
                col = row.column(align=True)
                col.operator("tlm_atlaslist.new_item", icon='ADD', text="")
                col.operator("tlm_atlaslist.delete_item", icon='REMOVE', text="")
                #col.menu("ARM_MT_BakeListSpecials", icon='DOWNARROW_HLT', text="")

                # if len(scene.TLM_AtlasList) > 1:
                #     col.separator()
                #     op = col.operator("arm_bakelist.move_item", icon='TRIA_UP', text="")
                #     op.direction = 'UP'
                #     op = col.operator("arm_bakelist.move_item", icon='TRIA_DOWN', text="")
                #     op.direction = 'DOWN'

                if atlasListItem >= 0 and len(atlasList) > 0:
                    item = atlasList[atlasListItem]
                    #layout.prop_search(item, "obj", bpy.data, "objects", text="Object")
                    #layout.prop(item, "res_x")
                    layout.prop(item, "tlm_atlas_lightmap_unwrap_mode")
                    layout.prop(item, "tlm_atlas_lightmap_resolution")
                    layout.prop(item, "tlm_atlas_unwrap_margin")

                    amount = 0

                    for obj in bpy.data.objects:
                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                                if obj.TLM_ObjectProperties.tlm_atlas_pointer == item.name:
                                    amount = amount + 1

                    layout.label(text="Objects: " + str(amount))

                # layout.use_property_split = True
                # layout.use_property_decorate = False
                # layout.label(text="Enable for selection")
                # layout.label(text="Disable for selection")
                # layout.label(text="Something...")

            else:

                layout.label(text="Postpacking is unstable.")
                rows = 2
                if len(atlasList) > 1:
                    rows = 4
                row = layout.row()
                row.template_list("TLM_UL_PostAtlasList", "PostList", scene, "TLM_PostAtlasList", scene, "TLM_PostAtlasListItem", rows=rows)
                col = row.column(align=True)
                col.operator("tlm_postatlaslist.new_item", icon='ADD', text="")
                col.operator("tlm_postatlaslist.delete_item", icon='REMOVE', text="")

                if postatlasListItem >= 0 and len(postatlasList) > 0:
                    item = postatlasList[postatlasListItem]
                    layout.prop(item, "tlm_atlas_lightmap_resolution")

                    #Below list object counter
                    amount = 0
                    utilized = 0
                    atlasUsedArea = 0
                    atlasSize = item.tlm_atlas_lightmap_resolution

                    for obj in bpy.data.objects:
                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                            if obj.TLM_ObjectProperties.tlm_postpack_object:
                                if obj.TLM_ObjectProperties.tlm_postatlas_pointer == item.name:
                                    amount = amount + 1

                                    atlasUsedArea += int(obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution) ** 2

                    row = layout.row()
                    row.prop(item, "tlm_atlas_repack_on_cleanup")

                    #TODO SET A CHECK FOR THIS! ADD A CV2 CHECK TO UTILITY!
                    cv2 = True

                    if cv2:
                        row = layout.row()
                        row.prop(item, "tlm_atlas_dilation")
                    layout.label(text="Objects: " + str(amount))

                    utilized = atlasUsedArea / (int(atlasSize) ** 2)
                    layout.label(text="Utilized: " + str(utilized * 100) + "%")

                    if (utilized * 100) > 100:
                        layout.label(text="Warning! Overflow not yet supported")

class ArmGenLodButton(bpy.types.Operator):
    '''Automatically generate LoD levels'''
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
        layout.prop(mdata, "arm_lod_screen_size")
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
        links.new(nodes['Principled BSDF'].inputs[17], nodes['Bump'].outputs[0])

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

class ARM_PT_ProxyPanel(bpy.types.Panel):
    bl_label = "Armory Proxy"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.operator("arm.make_proxy")
        obj = bpy.context.object
        if obj != None and obj.proxy != None:
            layout.label(text="Sync")
            layout.prop(obj, "arm_proxy_sync_loc")
            layout.prop(obj, "arm_proxy_sync_rot")
            layout.prop(obj, "arm_proxy_sync_scale")
            layout.prop(obj, "arm_proxy_sync_materials")
            layout.prop(obj, "arm_proxy_sync_modifiers")
            layout.prop(obj, "arm_proxy_sync_traits")
            row = layout.row()
            row.enabled = obj.arm_proxy_sync_traits
            row.prop(obj, "arm_proxy_sync_trait_props")
            layout.operator("arm.proxy_toggle_all")
            layout.operator("arm.proxy_apply_all")

class ArmMakeProxyButton(bpy.types.Operator):
    '''Create proxy from linked object'''
    bl_idname = 'arm.make_proxy'
    bl_label = 'Make Proxy'

    def execute(self, context):
        obj = context.object
        if obj == None:
            return{'CANCELLED'}
        if obj.library == None:
            self.report({'ERROR'}, 'Select linked object')
        arm.proxy.make(obj)
        return{'FINISHED'}

class ArmProxyToggleAllButton(bpy.types.Operator):
    bl_idname = 'arm.proxy_toggle_all'
    bl_label = 'Toggle All'
    def execute(self, context):
        obj = context.object
        b = not obj.arm_proxy_sync_loc
        obj.arm_proxy_sync_loc = b
        obj.arm_proxy_sync_rot = b
        obj.arm_proxy_sync_scale = b
        obj.arm_proxy_sync_materials = b
        obj.arm_proxy_sync_modifiers = b
        obj.arm_proxy_sync_traits = b
        obj.arm_proxy_sync_trait_props = b
        return{'FINISHED'}

class ArmProxyApplyAllButton(bpy.types.Operator):
    bl_idname = 'arm.proxy_apply_all'
    bl_label = 'Apply to All'

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.proxy == None:
                continue
            if obj.proxy == context.object.proxy:
                obj.arm_proxy_sync_loc = context.object.arm_proxy_sync_loc
                obj.arm_proxy_sync_rot = context.object.arm_proxy_sync_rot
                obj.arm_proxy_sync_scale = context.object.arm_proxy_sync_scale
                obj.arm_proxy_sync_materials = context.object.arm_proxy_sync_materials
                obj.arm_proxy_sync_modifiers = context.object.arm_proxy_sync_modifiers
                obj.arm_proxy_sync_traits = context.object.arm_proxy_sync_traits
                obj.arm_proxy_sync_trait_props = context.object.arm_proxy_sync_trait_props
        return{'FINISHED'}

class ArmSyncProxyButton(bpy.types.Operator):
    bl_idname = 'arm.sync_proxy'
    bl_label = 'Sync'
    def execute(self, context):
        if len(bpy.data.libraries) > 0:
            for obj in bpy.data.objects:
                if obj == None or obj.proxy == None:
                    continue
                if obj.arm_proxy_sync_loc:
                    arm.proxy.sync_location(obj)
                if obj.arm_proxy_sync_rot:
                    arm.proxy.sync_rotation(obj)
                if obj.arm_proxy_sync_scale:
                    arm.proxy.sync_scale(obj)
                if obj.arm_proxy_sync_materials:
                    arm.proxy.sync_materials(obj)
                if obj.arm_proxy_sync_modifiers:
                    arm.proxy.sync_modifiers(obj)
                if obj.arm_proxy_sync_traits:
                    arm.proxy.sync_traits(obj)
            print('Armory: Proxy objects synchronized')
        return{'FINISHED'}

class ArmPrintTraitsButton(bpy.types.Operator):
    bl_idname = 'arm.print_traits'
    bl_label = 'Print Traits'
    def execute(self, context):
        for s in bpy.data.scenes:
            print(s.name + ' traits:')
            for o in s.objects:
                for t in o.arm_traitlist:
                    if not t.enabled_prop:
                        continue
                    tname = t.node_tree_prop.name if t.type_prop == 'Logic Nodes' else t.class_name_prop
                    print('Object {0} - {1}'.format(o.name, tname))
        return{'FINISHED'}

class ARM_PT_MaterialNodePanel(bpy.types.Panel):
    bl_label = 'Armory Material Node'
    bl_idname = 'ARM_PT_MaterialNodePanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node'

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

class ARM_OT_ShowFileVersionInfo(bpy.types.Operator):
    bl_label = 'Show old file version info'
    bl_idname = 'arm.show_old_file_version_info'
    bl_description = ('Displays an info panel that warns about opening a file'
                       'which was created in a previous version of Armory')
    # bl_options = {'INTERNAL'}

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
        list_of_errors = arm.nodes_logic.replacement_errors.copy()
        # note: list_of_errors is a set of tuples: `(error_type, node_class, tree_name)`
        # where `error_type` can be "unregistered", "update failed", "future version", "bad version", or "misc."

        file_version = ARM_OT_ShowNodeUpdateErrors.wrd.arm_version
        current_version = props.arm_version

        # this will help order versions better, somewhat.
        # note: this is NOT complete
        current_version_2 = tuple( current_version.split('.') )
        file_version_2 = tuple( file_version.split('.') )
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

        layout.label(text="Some nodes failed to be updated to the current armory version", icon="ERROR")
        if current_version==file_version:
            layout.label(text="(This might be because you are using a development snapshot, or a homemade version ;) )", icon='BLANK1')
        elif not is_armory_upgrade:
            layout.label(text="(Please note that it is not possible do downgrade nodes to a previous version either.", icon='BLANK1')
            layout.label(text="This might be the cause of your problem.)", icon='BLANK1')

        layout.label(text=f'File saved in: {file_version}', icon='BLANK1')
        layout.label(text=f'Current version: {current_version}', icon='BLANK1')
        layout.separator()

        if 'update failed' in error_types:
            layout.label(text="Some nodes do not have an update procedure to deal with the version saved in this file.", icon='BLANK1')
            if current_version==file_version:
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
        # This allows for seamless migration from ealier versions of Armory
        for rp in wrd.arm_rplist: # TODO: deprecated
            if rp.rp_gi != 'Off':
                rp.rp_gi = 'Off'
                rp.rp_voxelao = True

        # Replace deprecated nodes
        arm.nodes_logic.replaceAll()

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
    '''Updating the list installed Visual Studio for the Windows platform'''
    bl_idname = 'arm.update_list_installed_vs'
    bl_label = 'Update List Installed Visual Studio'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}
        if not arm.utils.get_os_is_windows():
            return {"CANCELLED"}

        wrd = bpy.data.worlds['Arm']
        items, err = arm.utils.get_list_installed_vs_version()
        if len(err) > 0:
            print('Warning for operation Update List Installed Visual Studio: '+ err +'. Check if ArmorySDK is installed correctly.')
            return{'FINISHED'}
        if len(items) > 0:
            items_enum = [('10', '2010', 'Visual Studio 2010 (version 10)'),
                          ('11', '2012', 'Visual Studio 2012 (version 11)'),
                          ('12', '2013', 'Visual Studio 2013 (version 12)'),
                          ('14', '2015', 'Visual Studio 2015 (version 14)'),
                          ('15', '2017', 'Visual Studio 2017 (version 15)'),
                          ('16', '2019', 'Visual Studio 2019 (version 16)')]
            prev_select = wrd.arm_project_win_list_vs
            res_items_enum = []
            for vs in items_enum:
                l_vs = list(vs)
                for ver in items:
                    if l_vs[0] == ver[0]:
                        l_vs[1] = l_vs[1] + ' (installed)'
                        l_vs[2] = l_vs[2] + ' (installed)'
                        break
                res_items_enum.append((l_vs[0], l_vs[1], l_vs[2]))
            bpy.types.World.arm_project_win_list_vs = EnumProperty(items=res_items_enum, name="Visual Studio Version", default=prev_select, update=assets.invalidate_compiler_cache)
        return{'FINISHED'}

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
            layout.operator("arm.open_node_documentation", text="Show documentation for this node")
            layout.operator("arm.open_node_source", text="Open .hx source in the browser")
            layout.operator("arm.open_node_python_source", text="Open .py source in the browser")

    elif context.space_data.tree_type == 'ShaderNodeTree':
        if context.active_node.bl_idname in ('ShaderNodeRGB', 'ShaderNodeValue', 'ShaderNodeTexImage'):
            layout = self.layout
            layout.separator()
            layout.prop(context.active_node, 'arm_material_param', text='Armory: Material Parameter')


def register():
    bpy.utils.register_class(ARM_PT_ObjectPropsPanel)
    bpy.utils.register_class(ARM_PT_ModifiersPropsPanel)
    bpy.utils.register_class(ARM_PT_ParticlesPropsPanel)
    bpy.utils.register_class(ARM_PT_PhysicsPropsPanel)
    bpy.utils.register_class(ARM_PT_DataPropsPanel)
    bpy.utils.register_class(ARM_PT_ScenePropsPanel)
    bpy.utils.register_class(ARM_PT_WorldPropsPanel)
    bpy.utils.register_class(InvalidateCacheButton)
    bpy.utils.register_class(InvalidateMaterialCacheButton)
    bpy.utils.register_class(ARM_PT_MaterialPropsPanel)
    bpy.utils.register_class(ARM_PT_MaterialBlendingPropsPanel)
    bpy.utils.register_class(ARM_PT_MaterialDriverPropsPanel)
    bpy.utils.register_class(ARM_PT_ArmoryPlayerPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterAndroidSettingsPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterAndroidPermissionsPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterAndroidAbiPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterAndroidBuildAPKPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterHTML5SettingsPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterWindowsSettingsPanel)
    bpy.utils.register_class(ARM_PT_ArmoryProjectPanel)
    bpy.utils.register_class(ARM_PT_ProjectFlagsPanel)
    bpy.utils.register_class(ARM_PT_ProjectFlagsDebugConsolePanel)
    bpy.utils.register_class(ARM_PT_ProjectWindowPanel)
    bpy.utils.register_class(ARM_PT_ProjectModulesPanel)
    bpy.utils.register_class(ARM_PT_RenderPathPanel)
    bpy.utils.register_class(ARM_PT_RenderPathRendererPanel)
    bpy.utils.register_class(ARM_PT_RenderPathShadowsPanel)
    bpy.utils.register_class(ARM_PT_RenderPathVoxelsPanel)
    bpy.utils.register_class(ARM_PT_RenderPathWorldPanel)
    bpy.utils.register_class(ARM_PT_RenderPathPostProcessPanel)
    bpy.utils.register_class(ARM_PT_RenderPathCompositorPanel)
    bpy.utils.register_class(ARM_PT_BakePanel)
    # bpy.utils.register_class(ArmVirtualInputPanel)
    bpy.utils.register_class(ArmoryPlayButton)
    bpy.utils.register_class(ArmoryStopButton)
    bpy.utils.register_class(ArmoryBuildProjectButton)
    bpy.utils.register_class(ArmoryOpenProjectFolderButton)
    bpy.utils.register_class(ArmoryOpenEditorButton)
    bpy.utils.register_class(CleanMenu)
    bpy.utils.register_class(CleanButtonMenu)
    bpy.utils.register_class(ArmoryCleanProjectButton)
    bpy.utils.register_class(ArmoryPublishProjectButton)
    bpy.utils.register_class(ArmGenLodButton)
    bpy.utils.register_class(ARM_PT_LodPanel)
    bpy.utils.register_class(ArmGenTerrainButton)
    bpy.utils.register_class(ARM_PT_TerrainPanel)
    bpy.utils.register_class(ARM_PT_TilesheetPanel)
    bpy.utils.register_class(ARM_PT_ProxyPanel)
    bpy.utils.register_class(ArmMakeProxyButton)
    bpy.utils.register_class(ArmProxyToggleAllButton)
    bpy.utils.register_class(ArmProxyApplyAllButton)
    bpy.utils.register_class(ArmSyncProxyButton)
    bpy.utils.register_class(ArmPrintTraitsButton)
    bpy.utils.register_class(ARM_PT_MaterialNodePanel)
    bpy.utils.register_class(ARM_OT_UpdateFileSDK)
    bpy.utils.register_class(ARM_OT_ShowFileVersionInfo)
    bpy.utils.register_class(ARM_OT_ShowNodeUpdateErrors)
    bpy.utils.register_class(ARM_OT_DiscardPopup)
    bpy.utils.register_class(ArmoryUpdateListAndroidEmulatorButton)
    bpy.utils.register_class(ArmoryUpdateListAndroidEmulatorRunButton)
    bpy.utils.register_class(ArmoryUpdateListInstalledVSButton)

    bpy.types.VIEW3D_HT_header.append(draw_view3d_header)
    bpy.types.VIEW3D_MT_object.append(draw_view3d_object_menu)
    bpy.types.NODE_MT_context_menu.append(draw_custom_node_menu)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(draw_custom_node_menu)
    bpy.types.VIEW3D_MT_object.remove(draw_view3d_object_menu)
    bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)

    bpy.utils.unregister_class(ArmoryUpdateListInstalledVSButton)
    bpy.utils.unregister_class(ArmoryUpdateListAndroidEmulatorRunButton)
    bpy.utils.unregister_class(ArmoryUpdateListAndroidEmulatorButton)
    bpy.utils.unregister_class(ARM_OT_DiscardPopup)
    bpy.utils.unregister_class(ARM_OT_ShowNodeUpdateErrors)
    bpy.utils.unregister_class(ARM_OT_ShowFileVersionInfo)
    bpy.utils.unregister_class(ARM_OT_UpdateFileSDK)
    bpy.utils.unregister_class(ARM_PT_ObjectPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ModifiersPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ParticlesPropsPanel)
    bpy.utils.unregister_class(ARM_PT_PhysicsPropsPanel)
    bpy.utils.unregister_class(ARM_PT_DataPropsPanel)
    bpy.utils.unregister_class(ARM_PT_WorldPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ScenePropsPanel)
    bpy.utils.unregister_class(InvalidateCacheButton)
    bpy.utils.unregister_class(InvalidateMaterialCacheButton)
    bpy.utils.unregister_class(ARM_PT_MaterialDriverPropsPanel)
    bpy.utils.unregister_class(ARM_PT_MaterialBlendingPropsPanel)
    bpy.utils.unregister_class(ARM_PT_MaterialPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryPlayerPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterWindowsSettingsPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterHTML5SettingsPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterAndroidBuildAPKPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterAndroidAbiPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterAndroidPermissionsPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterAndroidSettingsPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryProjectPanel)
    bpy.utils.unregister_class(ARM_PT_ProjectFlagsDebugConsolePanel)
    bpy.utils.unregister_class(ARM_PT_ProjectFlagsPanel)
    bpy.utils.unregister_class(ARM_PT_ProjectWindowPanel)
    bpy.utils.unregister_class(ARM_PT_ProjectModulesPanel)
    bpy.utils.unregister_class(ARM_PT_RenderPathPanel)
    bpy.utils.unregister_class(ARM_PT_RenderPathRendererPanel)
    bpy.utils.unregister_class(ARM_PT_RenderPathShadowsPanel)
    bpy.utils.unregister_class(ARM_PT_RenderPathVoxelsPanel)
    bpy.utils.unregister_class(ARM_PT_RenderPathWorldPanel)
    bpy.utils.unregister_class(ARM_PT_RenderPathPostProcessPanel)
    bpy.utils.unregister_class(ARM_PT_RenderPathCompositorPanel)
    bpy.utils.unregister_class(ARM_PT_BakePanel)
    # bpy.utils.unregister_class(ArmVirtualInputPanel)
    bpy.utils.unregister_class(ArmoryPlayButton)
    bpy.utils.unregister_class(ArmoryStopButton)
    bpy.utils.unregister_class(ArmoryBuildProjectButton)
    bpy.utils.unregister_class(ArmoryOpenProjectFolderButton)
    bpy.utils.unregister_class(ArmoryOpenEditorButton)
    bpy.utils.unregister_class(CleanMenu)
    bpy.utils.unregister_class(CleanButtonMenu)
    bpy.utils.unregister_class(ArmoryCleanProjectButton)
    bpy.utils.unregister_class(ArmoryPublishProjectButton)
    bpy.utils.unregister_class(ArmGenLodButton)
    bpy.utils.unregister_class(ARM_PT_LodPanel)
    bpy.utils.unregister_class(ArmGenTerrainButton)
    bpy.utils.unregister_class(ARM_PT_TerrainPanel)
    bpy.utils.unregister_class(ARM_PT_TilesheetPanel)
    bpy.utils.unregister_class(ARM_PT_ProxyPanel)
    bpy.utils.unregister_class(ArmMakeProxyButton)
    bpy.utils.unregister_class(ArmProxyToggleAllButton)
    bpy.utils.unregister_class(ArmProxyApplyAllButton)
    bpy.utils.unregister_class(ArmSyncProxyButton)
    bpy.utils.unregister_class(ArmPrintTraitsButton)
    bpy.utils.unregister_class(ARM_PT_MaterialNodePanel)
