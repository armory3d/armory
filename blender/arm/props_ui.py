import bpy
import webbrowser
import os
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import arm.utils
import arm.make as make
import arm.make_state as state
import arm.assets as assets
import arm.log as log
import arm.proxy
import arm.api
import arm.props_properties

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
            layout.prop(obj, 'arm_rb_force_deactivation')
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
            pass

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
        if mat == None:
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
        if state.proc_play == None and state.proc_build == None:
            row.operator("arm.play", icon="PLAY")
        else:
            row.operator("arm.stop", icon="MESH_PLANE")
        row.operator("arm.clean_menu")
        layout.prop(wrd, 'arm_runtime')
        layout.prop(wrd, 'arm_play_camera')

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
        col.prop(wrd, 'arm_project_version')
        col.prop(wrd, 'arm_project_bundle')
        col.prop(wrd, 'arm_project_icon')
        col.prop(wrd, 'arm_dce')
        col.prop(wrd, 'arm_compiler_inline')
        col.prop(wrd, 'arm_minify_js')
        col.prop(wrd, 'arm_optimize_data')
        col.prop(wrd, 'arm_asset_compression')
        col.prop(wrd, 'arm_single_data_file')

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
        row.operator("arm.kode_studio")
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
        layout.prop(wrd, 'arm_debug_console')
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
        layout.prop(wrd, 'arm_winorient')
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

        webbrowser.open('file://' + arm.utils.get_fp())
        return{'FINISHED'}

class ArmoryKodeStudioButton(bpy.types.Operator):
    '''Launch this project in Kode Studio or VS Code'''
    bl_idname = 'arm.kode_studio'
    bl_label = 'Code Editor'
    bl_description = 'Open Project in IDE'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        arm.utils.check_default_props()

        if not os.path.exists(arm.utils.get_fp() + "/khafile.js"):
            print('Generating Krom project for Kode Studio')
            make.build('krom')

        arm.utils.kode_studio()
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
    if state.proc_build != None:
        self.layout.label(text='Compiling..')
    elif log.info_text != '':
        self.layout.label(text=log.info_text)

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
        col = layout.column()
        col.enabled = rpdat.arm_clouds
        col.prop(rpdat, 'arm_clouds_lower')
        col.prop(rpdat, 'arm_clouds_upper')
        col.prop(rpdat, 'arm_clouds_precipitation')
        col.prop(rpdat, 'arm_clouds_secondary')
        col.prop(rpdat, 'arm_clouds_wind')
        col.prop(rpdat, 'arm_clouds_steps')
        layout.prop(rpdat, "rp_water")
        col = layout.column()
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
        col = layout.column()
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

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        n = context.active_node
        if n != None and (n.bl_idname == 'ShaderNodeRGB' or n.bl_idname == 'ShaderNodeValue' or n.bl_idname == 'ShaderNodeTexImage'):
            layout.prop(context.active_node, 'arm_material_param')

def register():
    bpy.utils.register_class(ARM_PT_ObjectPropsPanel)
    bpy.utils.register_class(ARM_PT_ModifiersPropsPanel)
    bpy.utils.register_class(ARM_PT_ParticlesPropsPanel)
    bpy.utils.register_class(ARM_PT_PhysicsPropsPanel)
    bpy.utils.register_class(ARM_PT_DataPropsPanel)
    bpy.utils.register_class(ARM_PT_ScenePropsPanel)
    bpy.utils.register_class(InvalidateCacheButton)
    bpy.utils.register_class(InvalidateMaterialCacheButton)
    bpy.utils.register_class(ARM_PT_MaterialPropsPanel)
    bpy.utils.register_class(ARM_PT_MaterialBlendingPropsPanel)
    bpy.utils.register_class(ARM_PT_ArmoryPlayerPanel)
    bpy.utils.register_class(ARM_PT_ArmoryExporterPanel)
    bpy.utils.register_class(ARM_PT_ArmoryProjectPanel)
    bpy.utils.register_class(ARM_PT_ProjectFlagsPanel)
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
    bpy.utils.register_class(ArmoryKodeStudioButton)
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
    bpy.types.VIEW3D_HT_header.append(draw_view3d_header)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)
    bpy.utils.unregister_class(ARM_PT_ObjectPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ModifiersPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ParticlesPropsPanel)
    bpy.utils.unregister_class(ARM_PT_PhysicsPropsPanel)
    bpy.utils.unregister_class(ARM_PT_DataPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ScenePropsPanel)
    bpy.utils.unregister_class(InvalidateCacheButton)
    bpy.utils.unregister_class(InvalidateMaterialCacheButton)
    bpy.utils.unregister_class(ARM_PT_MaterialPropsPanel)
    bpy.utils.unregister_class(ARM_PT_MaterialBlendingPropsPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryPlayerPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryExporterPanel)
    bpy.utils.unregister_class(ARM_PT_ArmoryProjectPanel)
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
    bpy.utils.unregister_class(ArmoryKodeStudioButton)
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
