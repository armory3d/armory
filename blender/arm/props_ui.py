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

# Menu in object region
class ObjectPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return

        row = layout.row()
        row.prop(obj, 'arm_export')
        if not obj.arm_export:
            return
        row.prop(obj, 'arm_spawn')

        row = layout.row()
        row.prop(obj, 'arm_mobile')
        row.prop(obj, 'arm_animation_enabled')

        if bpy.app.version >= (2, 80, 1):
            layout.prop(obj, 'arm_visible')

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

class ModifiersPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return
        layout.operator("arm.invalidate_cache")

class ParticlesPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "particle"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.particle_system
        if obj == None:
            return

        layout.prop(obj.settings, 'arm_loop')
        layout.prop(obj.settings, 'arm_count_mult')

class PhysicsPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return

        if obj.rigid_body != None:
            # use_deactivation = obj.rigid_body.use_deactivation
            # layout.prop(obj.rigid_body, 'use_deactivation')
            # row = layout.row()
            # row.enabled = use_deactivation
            # row.prop(obj, 'arm_rb_deactivation_time')
            layout.prop(obj, 'arm_rb_linear_factor')
            layout.prop(obj, 'arm_rb_angular_factor')
            layout.prop(obj, 'arm_rb_trigger')
            layout.prop(obj, 'arm_rb_terrain')
            layout.prop(obj, 'arm_rb_force_deactivation')

        if obj.soft_body != None:
            layout.prop(obj, 'arm_soft_body_margin')

# Menu in data region
class DataPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return

        wrd = bpy.data.worlds['Arm']
        if obj.type == 'CAMERA':
            layout.prop(obj.data, 'arm_frustum_culling')
            layout.prop(obj.data, 'arm_render_to_texture')
            col = layout.column()
            col.enabled = obj.data.arm_render_to_texture
            row = col.row(align=True)
            row.label(text='Resolution')
            row.prop(obj.data, 'arm_texture_resolution_x')
            row.prop(obj.data, 'arm_texture_resolution_y')
        elif obj.type == 'MESH' or obj.type == 'FONT' or obj.type == 'META':
            row = layout.row(align=True)
            row.prop(obj.data, 'arm_dynamic_usage')
            row.prop(obj.data, 'arm_compress')
            # if obj.type == 'MESH':
                # layout.prop(obj.data, 'arm_sdfgen')
            layout.operator("arm.invalidate_cache")
        elif obj.type == 'LIGHT' or obj.type == 'LAMP': # TODO: LAMP is deprecated
            row = layout.row(align=True)
            col = row.column()
            col.prop(obj.data, 'arm_clip_start')
            col.prop(obj.data, 'arm_clip_end')
            col = row.column()
            col.prop(obj.data, 'arm_fov')
            col.prop(obj.data, 'arm_shadows_bias')
            layout.prop(wrd, 'arm_light_texture')
            layout.prop(wrd, 'arm_light_ies_texture')
            layout.prop(wrd, 'arm_light_clouds_texture')
        elif obj.type == 'SPEAKER':
            layout.prop(obj.data, 'arm_play_on_start')
            layout.prop(obj.data, 'arm_loop')
            layout.prop(obj.data, 'arm_stream')
        elif obj.type == 'ARMATURE':
            layout.prop(obj.data, 'arm_compress')

class ScenePropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        if scene == None:
            return
        row = layout.row()
        column = row.column()
        row.prop(scene, 'arm_export')
        row.prop(scene, 'arm_compress')
        # column.prop(scene, 'arm_gp_export')
        # columnb = column.column()
        # columnb.enabled = scene.arm_gp_export
        # columnb.operator('arm.invalidate_gp_cache')

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
        context.material.is_cached = False
        context.material.signature = ''
        return{'FINISHED'}

class InvalidateGPCacheButton(bpy.types.Operator):
    '''Delete cached grease pencil data'''
    bl_idname = "arm.invalidate_gp_cache"
    bl_label = "Invalidate GP Cache"

    def execute(self, context):
        if context.scene.grease_pencil != None:
            context.scene.grease_pencil.arm_cached = False
        return{'FINISHED'}

class MaterialPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        mat = bpy.context.material
        if mat == None:
            return

        row = layout.row()
        column = row.column()
        column.prop(mat, 'arm_cast_shadow')
        columnb = column.column()
        wrd = bpy.data.worlds['Arm']
        columnb.enabled = len(wrd.arm_rplist) > 0 and arm.utils.get_rp().rp_renderer == 'Forward'
        columnb.prop(mat, 'arm_receive_shadow')
        column.separator()
        column.prop(mat, 'arm_two_sided')
        columnb = column.column()
        columnb.enabled = not mat.arm_two_sided
        columnb.prop(mat, 'arm_cull_mode')
        columnb.prop(mat, 'arm_material_id')

        column = row.column()
        column.prop(mat, 'arm_overlay')
        column.prop(mat, 'arm_decal')

        column.separator()
        column.prop(mat, 'arm_discard')
        columnb = column.column(align=True)
        columnb.alignment = 'EXPAND'
        columnb.enabled = mat.arm_discard
        columnb.prop(mat, 'arm_discard_opacity')
        columnb.prop(mat, 'arm_discard_opacity_shadows')

        row = layout.row()
        col = row.column()
        col.label(text='Custom Material')
        col.prop(mat, 'arm_custom_material', text="")
        col = row.column()
        col.label(text='Skip Context')
        col.prop(mat, 'arm_skip_context', text="")

        row = layout.row()
        col = row.column()
        col.prop(mat, 'arm_particle_fade')
        col.prop(mat, 'arm_tilesheet_mat')
        col = row.column()
        col.label(text='Billboard')
        col.prop(mat, 'arm_billboard', text="")

        layout.prop(mat, 'arm_blending')
        col = layout.column()
        col.enabled = mat.arm_blending
        col.prop(mat, 'arm_blending_source')
        col.prop(mat, 'arm_blending_destination')
        col.prop(mat, 'arm_blending_operation')
        col.prop(mat, 'arm_blending_source_alpha')
        col.prop(mat, 'arm_blending_destination_alpha')
        col.prop(mat, 'arm_blending_operation_alpha')

        layout.operator("arm.invalidate_material_cache")

class ArmoryPlayerPanel(bpy.types.Panel):
    bl_label = "Armory Player"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        if state.proc_play == None and state.proc_build == None:
            row.operator("arm.play", icon="PLAY")
        else:
            row.operator("arm.stop", icon="MESH_PLANE")
        row.operator("arm.clean_menu")
        layout.prop(wrd, 'arm_play_runtime')
        layout.prop(wrd, 'arm_play_camera')

class ArmoryExporterPanel(bpy.types.Panel):
    bl_label = "Armory Exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
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
        row.template_list("ArmExporterList", "The_List", wrd, "arm_exporterlist", wrd, "arm_exporterlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_exporterlist.new_item", icon='ZOOMIN', text="")
        col.operator("arm_exporterlist.delete_item", icon='ZOOMOUT', text="")
        col.menu("arm_exporterlist_specials", icon='DOWNARROW_HLT', text="")

        if wrd.arm_exporterlist_index >= 0 and len(wrd.arm_exporterlist) > 0:
            item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
            box = layout.box().column()
            box.prop(item, 'arm_project_target')
            box.prop(item, arm.utils.target_to_gapi(item.arm_project_target))
            wrd.arm_rpcache_list.clear() # Make UIList work with prop_search()
            for i in wrd.arm_rplist:
                wrd.arm_rpcache_list.add().name = i.name
            box.prop_search(item, "arm_project_rp", wrd, "arm_rpcache_list", text="Render Path")
            if item.arm_project_scene == '':
                item.arm_project_scene = bpy.data.scenes[0].name
            box.prop_search(item, 'arm_project_scene', bpy.data, 'scenes', text='Scene')
            layout.separator()

        col = layout.column()
        col.prop(wrd, 'arm_project_name')
        col.prop(wrd, 'arm_project_package')
        col.prop(wrd, 'arm_project_version')
        col.prop(wrd, 'arm_project_bundle')
        col.prop(wrd, 'arm_project_icon')

class ArmoryProjectPanel(bpy.types.Panel):
    bl_label = "Armory Project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']

        row = layout.row(align=True)
        row.operator("arm.kode_studio")
        row.operator("arm.open_project_folder", icon="FILE_FOLDER")

        layout.label(text="Build")
        box = layout.box().column()
        row = box.row()
        col = row.column()
        col.prop(wrd, 'arm_play_console')
        col.prop(wrd, 'arm_dce')
        col.prop(wrd, 'arm_minify_js')
        col = row.column()
        col.prop(wrd, 'arm_cache_shaders')
        col.prop(wrd, 'arm_cache_compiler')
        col.prop(wrd, 'arm_gpu_processing')

        layout.label(text="Flags")
        box = layout.box().column()
        row = box.row()
        col = row.column()
        col.prop(wrd, 'arm_stream_scene')
        col.prop(wrd, 'arm_batch_meshes')
        col.prop(wrd, 'arm_batch_materials')
        col.prop(wrd, 'arm_sampled_animation')
        col.prop(wrd, 'arm_asset_compression')
        col.prop(wrd, 'arm_compiler_inline')
        col = row.column()
        col.prop(wrd, 'arm_minimize')
        col.prop(wrd, 'arm_optimize_mesh')
        col.prop(wrd, 'arm_deinterleaved_buffers')
        col.prop(wrd, 'arm_export_tangents')
        col.prop(wrd, 'arm_write_config')
        col.prop(wrd, 'arm_loadscreen')
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(wrd, 'arm_texture_quality')
        row.prop(wrd, 'arm_sound_quality')

        layout.label(text="Window")
        box = layout.box().column()
        row = box.row()
        row.prop(wrd, 'arm_winmode', expand=True)
        row = box.row()
        row.prop(wrd, 'arm_winorient', expand=True)
        row = box.row()
        col = row.column()
        col.prop(wrd, 'arm_winresize')
        col2 = col.column()
        col2.enabled = wrd.arm_winresize
        col2.prop(wrd, 'arm_winmaximize')
        col = row.column()
        col.prop(wrd, 'arm_winminimize')
        col.prop(wrd, 'arm_vsync')
        

        layout.label(text='Modules')
        box = layout.box().column()
        box.prop(wrd, 'arm_audio')
        box.prop(wrd, 'arm_physics')
        if wrd.arm_physics != 'Disabled':
            box.prop(wrd, 'arm_physics_engine')
        box.prop(wrd, 'arm_navigation')
        if wrd.arm_navigation != 'Disabled':
            box.prop(wrd, 'arm_navigation_engine')
        box.prop(wrd, 'arm_ui')
        box.prop(wrd, 'arm_hscript')
        box.prop(wrd, 'arm_formatlib')
        box.prop_search(wrd, 'arm_khafile', bpy.data, 'texts', text='Khafile')
        box.prop_search(wrd, 'arm_khamake', bpy.data, 'texts', text='Khamake')
        box.prop(wrd, 'arm_project_root')

        layout.label(text='Armory v' + wrd.arm_version)

class ArmVirtualInputPanel(bpy.types.Panel):
    bl_label = "Armory Virtual Input"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

class ArmNavigationPanel(bpy.types.Panel):
    bl_label = "Armory Navigation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        if scene == None:
            return

        layout.operator("arm.generate_navmesh")

class ArmoryGenerateNavmeshButton(bpy.types.Operator):
    '''Generate navmesh from selected meshes'''
    bl_idname = 'arm.generate_navmesh'
    bl_label = 'Generate Navmesh'

    def execute(self, context):
        obj = context.active_object
        if obj == None or obj.type != 'MESH':
            return{'CANCELLED'}

        # TODO: build tilecache here

    # Navmesh trait
        obj.arm_traitlist.add()
        obj.arm_traitlist[-1].type_prop = 'Bundled Script'
        obj.arm_traitlist[-1].class_name_prop = 'NavMesh'

        # For visualization
        bpy.ops.mesh.navmesh_make('EXEC_DEFAULT')
        obj = context.active_object
        obj.hide_render = True
        obj.arm_export = False

        return{'FINISHED'}

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

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        arm.utils.check_default_props()

        assets.invalidate_enabled = False
        make.play(is_viewport=False)
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

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        arm.utils.check_projectpath(self)

        arm.utils.check_default_props()

        wrd = bpy.data.worlds['Arm']
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        if item.arm_project_rp == '':
            item.arm_project_rp = wrd.arm_rplist[wrd.arm_rplist_index].name
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

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        self.report({'INFO'}, 'Publishing project, check console for details.')

        arm.utils.check_projectpath(self)

        arm.utils.check_default_props()

        wrd = bpy.data.worlds['Arm']
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        if item.arm_project_rp == '':
            item.arm_project_rp = wrd.arm_rplist[wrd.arm_rplist_index].name
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
    '''Launch this project in Kode Studio'''
    bl_idname = 'arm.kode_studio'
    bl_label = 'Kode Studio'
    bl_description = 'Open Project in Kode Studio'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

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

class ArmRenderPathPanel(bpy.types.Panel):
    bl_label = "Armory Render Path"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']

        rows = 2
        if len(wrd.arm_rplist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ArmRPList", "The_List", wrd, "arm_rplist", wrd, "arm_rplist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_rplist.new_item", icon='ZOOMIN', text="")
        col.operator("arm_rplist.delete_item", icon='ZOOMOUT', text="")

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
        
        layout.prop(wrd, "rp_preset")
        # layout.prop(wrd, "rp_search", icon="VIEWZOOM")

        layout.label(text='Renderer')
        box = layout.box().column()
        row = box.row()
        row.prop(rpdat, "rp_renderer", expand=True)
        col = box.column()
        col.enabled = rpdat.rp_renderer == 'Forward'
        col.prop(rpdat, 'rp_depthprepass')
        col.prop(rpdat, "arm_material_model")
        box.prop(rpdat, "rp_translucency_state")
        box.prop(rpdat, "rp_overlays_state")
        box.prop(rpdat, "rp_decals_state")
        box.prop(rpdat, "rp_blending_state")
        box.prop(rpdat, "rp_draw_order")
        box.prop(rpdat, 'arm_samples_per_pixel')
        box.prop(rpdat, 'arm_texture_filter')
        box.prop(rpdat, "arm_diffuse_model")
        box.prop(rpdat, "rp_sss_state")
        col = box.column()
        col.enabled = rpdat.rp_sss_state != 'Off'
        col.prop(rpdat, 'arm_sss_width')
        box.prop(rpdat, 'arm_rp_displacement')
        if rpdat.arm_rp_displacement == 'Tessellation':
            row = box.row()
            column = row.column()
            column.label(text='Mesh')
            columnb = column.column(align=True)
            columnb.prop(rpdat, 'arm_tess_mesh_inner')
            columnb.prop(rpdat, 'arm_tess_mesh_outer')

            column = row.column()
            column.label(text='Shadow')
            columnb = column.column(align=True)
            columnb.prop(rpdat, 'arm_tess_shadows_inner')
            columnb.prop(rpdat, 'arm_tess_shadows_outer')  

        box.prop(rpdat, 'arm_particles')
        box.prop(rpdat, 'arm_skin')
        row = box.row()
        row.enabled = rpdat.arm_skin.startswith('GPU')
        row.prop(rpdat, 'arm_skin_max_bones_auto')
        row = box.row()
        row.enabled = not rpdat.arm_skin_max_bones_auto
        row.prop(rpdat, 'arm_skin_max_bones')
        row = box.row()
        row.prop(rpdat, "rp_hdr")
        row.prop(rpdat, "rp_stereo")
        row.prop(rpdat, 'arm_culling')
        

        layout.label(text='Shadows')
        box = layout.box().column()
        box.prop(rpdat, 'rp_shadowmap')
        col = box.column()
        col.enabled = rpdat.rp_shadowmap != 'Off'
        col.prop(rpdat, 'rp_shadowmap_cascades')
        col2 = col.column()
        col2.enabled = rpdat.rp_shadowmap_cascades != '1'
        col2.prop(rpdat, 'arm_shadowmap_split')
        col.prop(rpdat, 'arm_shadowmap_bounds')
        col.prop(rpdat, 'arm_soft_shadows')
        col2 = col.column()
        col2.enabled = rpdat.arm_soft_shadows != 'Off'
        row = col2.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_soft_shadows_penumbra')
        row.prop(rpdat, 'arm_soft_shadows_distance')
        col.prop(rpdat, 'arm_pcfsize')


        layout.label(text='Global Illumination')
        box = layout.box().column()
        row = box.row()
        row.prop(rpdat, 'rp_gi', expand=True)
        col = box.column()
        col.enabled = rpdat.rp_gi != 'Off'
        col2 = col.column()
        col2.enabled = rpdat.rp_gi == 'Voxel GI'
        col2.prop(rpdat, 'arm_voxelgi_bounces')
        row2 = col2.row()
        row2.prop(rpdat, 'rp_voxelgi_relight')
        row2.prop(rpdat, 'rp_voxelgi_hdr', text='HDR')
        row2 = col2.row()
        row2.prop(rpdat, 'arm_voxelgi_refraction', text='Refraction')
        row2.prop(rpdat, 'arm_voxelgi_shadows', text='Shadows')
        col.prop(rpdat, 'arm_voxelgi_cones')
        col.prop(rpdat, 'rp_voxelgi_resolution')
        col.prop(rpdat, 'rp_voxelgi_resolution_z')
        col.prop(rpdat, 'arm_voxelgi_dimensions')
        col.prop(rpdat, 'arm_voxelgi_revoxelize')
        row2 = col.row()
        row2.enabled = rpdat.arm_voxelgi_revoxelize
        row2.prop(rpdat, 'arm_voxelgi_camera')
        row2.prop(rpdat, 'arm_voxelgi_temporal')
        col.label(text="Light")
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.enabled = rpdat.rp_gi == 'Voxel GI'
        row.prop(rpdat, 'arm_voxelgi_diff')
        row.prop(rpdat, 'arm_voxelgi_spec')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_voxelgi_occ')
        row.prop(rpdat, 'arm_voxelgi_env')
        col.label(text="Ray")
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_voxelgi_step')
        row.prop(rpdat, 'arm_voxelgi_range')
        col.prop(rpdat, 'arm_voxelgi_offset')

        layout.label(text='World')
        box = layout.box().column()
        row = box.row()
        row.prop(rpdat, "rp_background", expand=True)
        row = box.row()
        row.prop(rpdat, 'arm_irradiance')
        col = row.column()
        col.enabled = rpdat.arm_irradiance
        col.prop(rpdat, 'arm_radiance')
        row = box.row()
        row.enabled = rpdat.arm_irradiance
        col = row.column()
        col.prop(rpdat, 'arm_radiance_sky')
        colb = row.column()
        colb.enabled = rpdat.arm_radiance
        colb.prop(rpdat, 'arm_radiance_size')
        box.prop(rpdat, 'arm_clouds')
        col = box.column()
        col.enabled = rpdat.arm_clouds
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_clouds_density')
        row.prop(rpdat, 'arm_clouds_size')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_clouds_lower')
        row.prop(rpdat, 'arm_clouds_upper')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_clouds_precipitation')
        row.prop(rpdat, 'arm_clouds_eccentricity')
        col.prop(rpdat, 'arm_clouds_secondary')
        row = col.row()
        row.prop(rpdat, 'arm_clouds_wind')
        box.prop(rpdat, "rp_ocean")
        col = box.column()
        col.enabled = rpdat.rp_ocean
        col.prop(rpdat, 'arm_ocean_level')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_ocean_fade')
        row.prop(rpdat, 'arm_ocean_amplitude')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_ocean_height')
        row.prop(rpdat, 'arm_ocean_choppy')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_ocean_speed')
        row.prop(rpdat, 'arm_ocean_freq')
        row = col.row()
        col2 = row.column()
        col2.prop(rpdat, 'arm_ocean_base_color')
        col2 = row.column()
        col2.prop(rpdat, 'arm_ocean_water_color')


        layout.separator()
        layout.prop(rpdat, "rp_render_to_texture")
        box = layout.box().column()
        box.enabled = rpdat.rp_render_to_texture
        row = box.row()
        row.prop(rpdat, "rp_antialiasing", expand=True)
        box.prop(rpdat, "rp_supersampling")
        box.prop(rpdat, 'arm_rp_resolution')
        if rpdat.arm_rp_resolution == 'Custom':
            box.prop(rpdat, 'arm_rp_resolution_size')
            box.prop(rpdat, 'arm_rp_resolution_filter')
        box.prop(rpdat, 'rp_dynres')
        box.separator()
        row = box.row()
        row.prop(rpdat, "rp_ssgi", expand=True)
        col = box.column()
        col.enabled = rpdat.rp_ssgi != 'Off'
        col.prop(rpdat, 'arm_ssgi_rays')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_ssgi_step')
        row.prop(rpdat, 'arm_ssgi_strength')
        col.prop(rpdat, 'arm_ssgi_max_steps')
        box.separator()
        box.prop(rpdat, "rp_ssr")
        col = box.column()
        col.enabled = rpdat.rp_ssr
        row = col.row(align=True)
        row.prop(rpdat, 'arm_ssr_half_res')
        row.prop(rpdat, 'rp_ssr_z_only')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_ssr_ray_step')
        row.prop(rpdat, 'arm_ssr_min_ray_step')
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_ssr_search_dist')
        row.prop(rpdat, 'arm_ssr_falloff_exp')
        col.prop(rpdat, 'arm_ssr_jitter')
        box.separator()
        box.prop(rpdat, 'arm_ssrs')
        col = box.column()
        col.enabled = rpdat.arm_ssrs
        col.prop(rpdat, 'arm_ssrs_ray_step')
        box.separator()
        box.prop(rpdat, "rp_bloom")
        col = box.column()
        col.enabled = rpdat.rp_bloom
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_bloom_threshold')
        row.prop(rpdat, 'arm_bloom_strength')
        col.prop(rpdat, 'arm_bloom_radius')
        box.separator()
        box.prop(rpdat, "rp_motionblur")
        col = box.column()
        col.enabled = rpdat.rp_motionblur != 'Off'
        col.prop(rpdat, 'arm_motion_blur_intensity')
        box.separator()
        box.prop(rpdat, "rp_volumetriclight")
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.enabled = rpdat.rp_volumetriclight
        row.prop(rpdat, 'arm_volumetric_light_air_color', text="")
        row.prop(rpdat, 'arm_volumetric_light_air_turbidity', text="Turbidity")
        row.prop(rpdat, 'arm_volumetric_light_steps', text="Steps")


        layout.separator()
        layout.prop(rpdat, "rp_compositornodes")
        box = layout.box().column()
        box.enabled = rpdat.rp_compositornodes
        box.prop(rpdat, 'arm_tonemap')
        box.prop(rpdat, 'arm_letterbox')
        col = box.column()
        col.enabled = rpdat.arm_letterbox
        col.prop(rpdat, 'arm_letterbox_size')
        box.prop(rpdat, 'arm_sharpen')
        col = box.column()
        col.enabled = rpdat.arm_sharpen
        col.prop(rpdat, 'arm_sharpen_strength')
        box.prop(rpdat, 'arm_fisheye')
        box.prop(rpdat, 'arm_vignette')
        box.prop(rpdat, 'arm_lensflare')
        box.prop(rpdat, 'arm_grain')
        col = box.column()
        col.enabled = rpdat.arm_grain
        col.prop(rpdat, 'arm_grain_strength')
        box.prop(rpdat, 'arm_fog')
        col = box.column()
        col.enabled = rpdat.arm_fog
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(rpdat, 'arm_fog_color', text="")
        row.prop(rpdat, 'arm_fog_amounta', text="A")
        row.prop(rpdat, 'arm_fog_amountb', text="B")
        box.separator()
        box.prop(rpdat, "rp_autoexposure")
        col = box.column()
        col.enabled = rpdat.rp_autoexposure
        col.prop(rpdat, 'arm_autoexposure_strength', text='Strength')
        box.prop(rpdat, 'arm_lens_texture')
        box.prop(rpdat, 'arm_lut_texture')

class ArmBakePanel(bpy.types.Panel):
    bl_label = "Armory Bake"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("arm.bake_textures", icon="RENDER_STILL")
        row.operator("arm.bake_apply")

        row = layout.row()
        col = row.column()
        col.label(text='Lightmaps:')
        col.prop(scn, 'arm_bakelist_scale')

        col = row.column()
        col.label(text="Samples:")
        col.prop(scn.cycles, "samples", text="Render")

        layout.prop(scn, 'arm_bakelist_unwrap')

        rows = 2
        if len(scn.arm_bakelist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ArmBakeList", "The_List", scn, "arm_bakelist", scn, "arm_bakelist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_bakelist.new_item", icon='ZOOMIN', text="")
        col.operator("arm_bakelist.delete_item", icon='ZOOMOUT', text="")
        col.menu("arm_bakelist_specials", icon='DOWNARROW_HLT', text="")

        if scn.arm_bakelist_index >= 0 and len(scn.arm_bakelist) > 0:
            item = scn.arm_bakelist[scn.arm_bakelist_index]
            box = layout.box().column()
            row = box.row()
            row.prop_search(item, "object_name", scn, "objects", text="Object")
            col = row.column(align=True)
            col.alignment = 'EXPAND'
            col.prop(item, "res_x")
            col.prop(item, "res_y")

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
            new_obj.hide = True
            new_obj.hide_render = True
            mod = new_obj.modifiers.new('Decimate', 'DECIMATE')
            mod.ratio = ratio
            ratio *= wrd.arm_lod_gen_ratio
            context.scene.objects.link(new_obj)

        # Screen sizes
        for level in range(0, num_levels):
            mdata.arm_lodlist.add()
            mdata.arm_lodlist[-1].name = self.lod_name(obj.name, level)
            mdata.arm_lodlist[-1].screen_size_prop = (1 - (1 / (num_levels + 1)) * level) - (1 / (num_levels + 1))

        return{'FINISHED'}

class ArmLodPanel(bpy.types.Panel):
    bl_label = "Armory Lod"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object

        # Mesh only for now
        if obj.type != 'MESH':
            return

        mdata = obj.data

        rows = 2
        if len(mdata.arm_lodlist) > 1:
            rows = 4

        row = layout.row()
        row.template_list("ArmLodList", "The_List", mdata, "arm_lodlist", mdata, "arm_lodlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_lodlist.new_item", icon='ZOOMIN', text="")
        col.operator("arm_lodlist.delete_item", icon='ZOOMOUT', text="")

        if mdata.arm_lodlist_index >= 0 and len(mdata.arm_lodlist) > 0:
            item = mdata.arm_lodlist[mdata.arm_lodlist_index]
            row = layout.row()
            row.prop_search(item, "name", bpy.data, "objects", text="Object")
            row = layout.row()
            row.prop(item, "screen_size_prop")

        layout.prop(mdata, "arm_lod_material")

        # Auto lod for meshes
        if obj.type == 'MESH':
            layout.separator()
            layout.operator("arm.generate_lod")
            wrd = bpy.data.worlds['Arm']
            row = layout.row()
            row.prop(wrd, 'arm_lod_gen_levels')
            row.prop(wrd, 'arm_lod_gen_ratio')

        

class ArmTilesheetPanel(bpy.types.Panel):
    bl_label = "Armory Tilesheet"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']

        rows = 2
        if len(wrd.arm_tilesheetlist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ArmTilesheetList", "The_List", wrd, "arm_tilesheetlist", wrd, "arm_tilesheetlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_tilesheetlist.new_item", icon='ZOOMIN', text="")
        col.operator("arm_tilesheetlist.delete_item", icon='ZOOMOUT', text="")

        if wrd.arm_tilesheetlist_index >= 0 and len(wrd.arm_tilesheetlist) > 0:
            dat = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
            row = layout.row()
            row.prop(dat, "tilesx_prop")
            row.prop(dat, "tilesy_prop")
            layout.prop(dat, "framerate_prop")

            layout.label(text='Actions')
            rows = 2
            if len(dat.arm_tilesheetactionlist) > 1:
                rows = 4
            row = layout.row()
            row.template_list("ArmTilesheetList", "The_List", dat, "arm_tilesheetactionlist", dat, "arm_tilesheetactionlist_index", rows=rows)
            col = row.column(align=True)
            col.operator("arm_tilesheetactionlist.new_item", icon='ZOOMIN', text="")
            col.operator("arm_tilesheetactionlist.delete_item", icon='ZOOMOUT', text="")

            if dat.arm_tilesheetactionlist_index >= 0 and len(dat.arm_tilesheetactionlist) > 0:
                adat = dat.arm_tilesheetactionlist[dat.arm_tilesheetactionlist_index]
                row = layout.row()
                row.prop(adat, "start_prop")
                row.prop(adat, "end_prop")
                layout.prop(adat, "loop_prop")

class ArmProxyPanel(bpy.types.Panel):
    bl_label = "Armory Proxy"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator("arm.make_proxy")
        obj = bpy.context.object
        if obj != None and obj.proxy != None:
            layout.label(text="Sync")
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(obj, "arm_proxy_sync_loc")
            row.prop(obj, "arm_proxy_sync_rot")
            row.prop(obj, "arm_proxy_sync_scale")
            row = col.row(align=True)
            row.prop(obj, "arm_proxy_sync_materials")
            row.prop(obj, "arm_proxy_sync_modifiers")
            row.prop(obj, "arm_proxy_sync_traits")
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("arm.proxy_toggle_all")
            row.operator("arm.proxy_apply_all")

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
                    tname = t.nodes_name_prop if t.type_prop == 'Logic Nodes' else t.class_name_prop
                    print('Object {0} - {1}'.format(o.name, tname))
        return{'FINISHED'}

class ArmMaterialNodePanel(bpy.types.Panel):
    bl_label = 'Armory Material Node'
    bl_idname = 'ArmMaterialNodePanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        n = context.active_node
        if n != None and (n.bl_idname == 'ShaderNodeRGB' or n.bl_idname == 'ShaderNodeValue' or n.bl_idname == 'ShaderNodeTexImage'):
            layout.prop(context.active_node, 'arm_material_param')

def register():
    bpy.utils.register_class(ObjectPropsPanel)
    bpy.utils.register_class(ModifiersPropsPanel)
    bpy.utils.register_class(ParticlesPropsPanel)
    bpy.utils.register_class(PhysicsPropsPanel)
    bpy.utils.register_class(DataPropsPanel)
    bpy.utils.register_class(ScenePropsPanel)
    bpy.utils.register_class(InvalidateCacheButton)
    bpy.utils.register_class(InvalidateMaterialCacheButton)
    bpy.utils.register_class(InvalidateGPCacheButton)
    bpy.utils.register_class(MaterialPropsPanel)
    bpy.utils.register_class(ArmoryPlayerPanel)
    bpy.utils.register_class(ArmoryExporterPanel)
    bpy.utils.register_class(ArmoryProjectPanel)
    bpy.utils.register_class(ArmRenderPathPanel)
    bpy.utils.register_class(ArmBakePanel)
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
    bpy.utils.register_class(ArmoryGenerateNavmeshButton)
    bpy.utils.register_class(ArmNavigationPanel)
    bpy.utils.register_class(ArmGenLodButton)
    bpy.utils.register_class(ArmLodPanel)
    bpy.utils.register_class(ArmTilesheetPanel)
    bpy.utils.register_class(ArmProxyPanel)
    bpy.utils.register_class(ArmMakeProxyButton)
    bpy.utils.register_class(ArmProxyToggleAllButton)
    bpy.utils.register_class(ArmProxyApplyAllButton)
    bpy.utils.register_class(ArmSyncProxyButton)
    bpy.utils.register_class(ArmPrintTraitsButton)
    bpy.utils.register_class(ArmMaterialNodePanel)
    bpy.types.VIEW3D_HT_header.append(draw_view3d_header)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)
    bpy.utils.unregister_class(ObjectPropsPanel)
    bpy.utils.unregister_class(ModifiersPropsPanel)
    bpy.utils.unregister_class(ParticlesPropsPanel)
    bpy.utils.unregister_class(PhysicsPropsPanel)
    bpy.utils.unregister_class(DataPropsPanel)
    bpy.utils.unregister_class(ScenePropsPanel)
    bpy.utils.unregister_class(InvalidateCacheButton)
    bpy.utils.unregister_class(InvalidateMaterialCacheButton)
    bpy.utils.unregister_class(InvalidateGPCacheButton)
    bpy.utils.unregister_class(MaterialPropsPanel)
    bpy.utils.unregister_class(ArmoryPlayerPanel)
    bpy.utils.unregister_class(ArmoryExporterPanel)
    bpy.utils.unregister_class(ArmoryProjectPanel)
    bpy.utils.unregister_class(ArmRenderPathPanel)
    bpy.utils.unregister_class(ArmBakePanel)
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
    bpy.utils.unregister_class(ArmoryGenerateNavmeshButton)
    bpy.utils.unregister_class(ArmNavigationPanel)
    bpy.utils.unregister_class(ArmGenLodButton)
    bpy.utils.unregister_class(ArmLodPanel)
    bpy.utils.unregister_class(ArmTilesheetPanel)
    bpy.utils.unregister_class(ArmProxyPanel)
    bpy.utils.unregister_class(ArmMakeProxyButton)
    bpy.utils.unregister_class(ArmProxyToggleAllButton)
    bpy.utils.unregister_class(ArmProxyApplyAllButton)
    bpy.utils.unregister_class(ArmSyncProxyButton)
    bpy.utils.unregister_class(ArmPrintTraitsButton)
    bpy.utils.unregister_class(ArmMaterialNodePanel)
