import bpy
import webbrowser
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import arm.utils
import arm.make_renderer as make_renderer
import arm.make as make
import arm.make_utils as make_utils
import arm.make_state as state
import arm.assets as assets
import arm.log as log
import arm.proxy

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

        if obj.type == 'MESH':
            layout.prop(obj, 'arm_instanced')
            if obj.arm_instanced:
                layout.label('Location')
                column = layout.column()
                column.prop(obj, 'arm_instanced_loc_x')
                column.prop(obj, 'arm_instanced_loc_y')
                column.prop(obj, 'arm_instanced_loc_z')
                # layout.label('Rotation')
                # row = layout.row()
                # row.prop(obj, 'arm_instanced')
                # row.prop(obj, 'arm_instanced')
                # row.prop(obj, 'arm_instanced')
                # layout.label('Scale')
                # row = layout.row()
                # row.prop(obj, 'arm_instanced')
                # row.prop(obj, 'arm_instanced')
                # row.prop(obj, 'arm_instanced')

            wrd = bpy.data.worlds['Arm']
            layout.prop_search(obj, "arm_tilesheet", wrd, "arm_tilesheetlist", "Tilesheet")
            if obj.arm_tilesheet != '':
                selected_ts = None
                for ts in wrd.arm_tilesheetlist:
                    if ts.name == obj.arm_tilesheet:
                        selected_ts = ts
                        break
                layout.prop_search(obj, "arm_tilesheet_action", selected_ts, "arm_tilesheetactionlist", "Action")

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

        # Assume as first modifier
        if len(obj.modifiers) > 0 and obj.modifiers[0].type == 'OCEAN':
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_base_color')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_water_color')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_fade')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_amplitude')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_height')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_choppy')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_speed')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_freq')
            layout.prop(bpy.data.worlds['Arm'], 'arm_ocean_fade')

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
        layout.prop(obj.settings, 'arm_gpu_sim')
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

        layout.prop(obj, 'arm_rb_linear_factor')
        layout.prop(obj, 'arm_rb_angular_factor')
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
            row.label('Resolution')
            row.prop(obj.data, 'arm_texture_resolution_x')
            row.prop(obj.data, 'arm_texture_resolution_y')
        elif obj.type == 'MESH' or obj.type == 'FONT' or obj.type == 'META':
            row = layout.row(align=True)
            row.prop(obj.data, 'arm_dynamic_usage')
            row.prop(obj.data, 'arm_compress')
            if obj.type == 'MESH':
                layout.prop(obj.data, 'arm_sdfgen')
            layout.operator("arm.invalidate_cache")
        elif obj.type == 'LAMP':
            row = layout.row(align=True)
            col = row.column()
            col.prop(obj.data, 'arm_clip_start')
            col.prop(obj.data, 'arm_clip_end')
            col = row.column()
            col.prop(obj.data, 'arm_fov')
            col.prop(obj.data, 'arm_shadows_bias')
            if obj.data.type == 'POINT':
                layout.prop(obj.data, 'arm_omni_shadows')
                col = layout.column()
                col.enabled = obj.data.arm_omni_shadows
                col.prop(wrd, 'arm_pcfsize')
            layout.prop(wrd, 'arm_lamp_texture')
            layout.prop(wrd, 'arm_lamp_ies_texture')
            layout.prop(wrd, 'arm_lamp_clouds_texture')
        elif obj.type == 'SPEAKER':
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
        column.prop(scene, 'arm_export')
        column.prop(scene, 'arm_compress')
        column = row.column()
        column.prop(scene, 'arm_gp_export')
        columnb = column.column()
        columnb.enabled = scene.arm_gp_export
        columnb.operator('arm.invalidate_gp_cache')

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
        column.prop(mat, 'arm_receive_shadow')
        column.separator()
        column.prop(mat, 'arm_two_sided')
        columnb = column.column()
        columnb.enabled = not mat.arm_two_sided
        columnb.prop(mat, 'arm_cull_mode')

        column = row.column()
        column.prop(mat, 'arm_overlay')
        column.prop(mat, 'arm_decal')

        column.separator()
        column.prop(mat, 'arm_discard')
        columnb = column.column()
        columnb.enabled = mat.arm_discard
        columnb.prop(mat, 'arm_discard_opacity')
        columnb.prop(mat, 'arm_discard_opacity_shadows')

        layout.separator()
        row = layout.row()
        column = row.column()
        column.prop(mat, 'arm_tess')
        columnb = column.column()
        columnb.enabled = mat.arm_tess
        columnb.prop(mat, 'arm_tess_inner')
        columnb.prop(mat, 'arm_tess_outer')

        column = row.column()
        column.prop(mat, 'arm_tess_shadows')
        columnb = column.column()
        columnb.enabled = mat.arm_tess_shadows
        columnb.prop(mat, 'arm_tess_shadows_inner')
        columnb.prop(mat, 'arm_tess_shadows_outer')

        layout.prop(mat, 'arm_custom_material')
        layout.prop(mat, 'arm_skip_context')
        layout.prop(mat, 'arm_billboard')
        layout.prop(mat, 'arm_particle')
        if mat.arm_particle == 'gpu':
            layout.prop(mat, 'arm_particle_fade')
        row = layout.row()
        row.prop(mat, 'arm_tilesheet_mat')
        row.prop(mat, 'arm_blending')

        layout.operator("arm.invalidate_material_cache")

class WorldPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"

    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']

        layout.prop(wrd, 'arm_irradiance')
        row = layout.row()
        row.enabled = wrd.arm_irradiance
        column = row.column()
        column.prop(wrd, 'arm_radiance')
        columnb = column.column()
        columnb.enabled = wrd.arm_radiance
        columnb.prop(wrd, 'arm_radiance_size')
        column = row.column()
        column.prop(wrd, 'arm_radiance_sky')
        columnb = column.column()
        columnb.enabled = wrd.arm_radiance_sky
        columnb.prop(wrd, 'arm_radiance_sky_type')

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
        if state.playproc == None and state.compileproc == None:
            row.operator("arm.play", icon="PLAY")
        else:
            row.operator("arm.stop", icon="MESH_PLANE")
        if state.playproc == None and state.krom_running == False:
            row.operator("arm.build")
        else:
            row.operator("arm.patch")
        row.operator("arm.clean_menu")

        layout.prop(wrd, 'arm_play_runtime')
        layout.prop(wrd, 'arm_play_camera')

class ArmoryRenderPanel(bpy.types.Panel):
    bl_label = "Armory Render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("arm.render", icon="RENDER_STILL")
        row.operator("arm.render_anim", icon="RENDER_ANIMATION")
        layout.prop(bpy.data.worlds['Arm'], "rp_rendercapture_format")
        if bpy.context.scene != None:
            layout.prop(bpy.context.scene.render, "filepath")

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
        row.operator("arm.patch_project")
        row.operator("arm.publish_project")
        row.enabled = wrd.arm_exporterlist_index >= 0 and len(wrd.arm_exporterlist) > 0

        rows = 2
        if len(wrd.arm_exporterlist) > 1:
            rows = 4
        row = layout.row()
        row.template_list("ArmExporterList", "The_List", wrd, "arm_exporterlist", wrd, "arm_exporterlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("arm_exporterlist.new_item", icon='ZOOMIN', text="")
        col.operator("arm_exporterlist.delete_item", icon='ZOOMOUT', text="")

        if wrd.arm_exporterlist_index >= 0 and len(wrd.arm_exporterlist) > 0:
            item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
            layout.prop(item, 'arm_project_target')
            layout.prop(item, make_utils.target_to_gapi(item.arm_project_target))
            wrd.arm_rpcache_list.clear() # Make UIList work with prop_search()
            for i in wrd.arm_rplist:
                wrd.arm_rpcache_list.add().name = i.name
            layout.prop_search(item, "arm_project_rp", wrd, "arm_rpcache_list", "Render Path")

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
        row.operator("arm.open_project_folder")

        layout.label('Build:')
        row = layout.row()
        col = row.column()

        col.prop(wrd, 'arm_play_console')
        col.prop(wrd, 'arm_stream_scene')

        if arm.utils.with_krom():
            col.prop(wrd, 'arm_play_live_patch')
            colb = col.column()
            colb.enabled = wrd.arm_play_live_patch
            colb.prop(wrd, 'arm_play_auto_build')

        col = row.column()
        col.prop(wrd, 'arm_cache_shaders')
        col.prop(wrd, 'arm_cache_compiler')
        col.prop(wrd, 'arm_gpu_processing')

        layout.label('Flags:')
        row = layout.row()
        col = row.column()
        col.prop(wrd, 'arm_batch_meshes')
        col.prop(wrd, 'arm_batch_materials')
        col.prop(wrd, 'arm_sampled_animation')
        col.prop(wrd, 'arm_dce')
        col.prop(wrd, 'arm_play_active_scene')
        if not wrd.arm_play_active_scene:
            col.prop_search(wrd, 'arm_project_scene', bpy.data, 'scenes', '')

        col = row.column()
        col.prop(wrd, 'arm_minimize')
        col.prop(wrd, 'arm_optimize_mesh')
        col.prop(wrd, 'arm_deinterleaved_buffers')
        col.prop(wrd, 'arm_export_tangents')
        col.prop(wrd, 'arm_asset_compression')

        layout.label('Window:')
        row = layout.row()
        col = row.column()
        col.prop(wrd, 'arm_vsync')
        col.prop(wrd, 'arm_loadbar')
        col.prop(wrd, 'arm_winmode')

        col = row.column()
        col.prop(wrd, 'arm_winresize')
        col.prop(wrd, 'arm_winmaximize')
        col.prop(wrd, 'arm_winminimize')

        layout.prop(wrd, 'arm_winorient')

        layout.label('Assets:')
        layout.prop(wrd, 'arm_texture_quality')
        layout.prop(wrd, 'arm_sound_quality')

        layout.separator()
        layout.label('Modules:')
        layout.prop(wrd, 'arm_physics')
        layout.prop(wrd, 'arm_navigation')
        layout.prop(wrd, 'arm_ui')
        layout.prop(wrd, 'arm_hscript')

        layout.separator()
        layout.label('Project:')
        layout.prop(wrd, 'arm_project_name')
        layout.prop(wrd, 'arm_project_package')
        layout.prop_search(wrd, 'arm_khafile', bpy.data, 'texts', 'Khafile')
        layout.prop_search(wrd, 'arm_khamake', bpy.data, 'texts', 'Khamake')
        layout.prop(wrd, 'arm_project_root')

        layout.label('Armory v' + wrd.arm_version)

class ArmVirtualInputPanel(bpy.types.Panel):
    bl_label = "Armory Virtual Input"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

class ArmGlobalVarsPanel(bpy.types.Panel):
    bl_label = "Armory Global Variables"
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
        if state.compileproc != None:
            return {"CANCELLED"}

        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        make_renderer.check_default()

        rpdat = arm.utils.get_rp()
        if rpdat.rp_rendercapture == True:
            rpdat.rp_rendercapture = False

        state.is_export = False
        assets.invalidate_enabled = False
        make.play_project(False)
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryPlayInViewportButton(bpy.types.Operator):
    '''Launch player in 3D viewport'''
    bl_idname = 'arm.play_in_viewport'
    bl_label = 'Play in Viewport'

    def execute(self, context):
        if state.compileproc != None:
            return {"CANCELLED"}

        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        if context.area == None:
            return {"CANCELLED"}

        make_renderer.check_default()

        rpdat = arm.utils.get_rp()
        if rpdat.rp_rendercapture == True:
            rpdat.rp_rendercapture = False

        state.is_export = False
        assets.invalidate_enabled = False
        if state.playproc == None and state.krom_running == False:
            if context.area.type != 'VIEW_3D':
                return {"CANCELLED"}
            # Cancel viewport render
            for space in context.area.spaces:
                if space.type == 'VIEW_3D':
                    if space.viewport_shade == 'RENDERED':
                        space.viewport_shade = 'SOLID'
                    break
            make.play_project(True)
        else:
            make.play_project(True)
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryStopButton(bpy.types.Operator):
    '''Stop currently running player'''
    bl_idname = 'arm.stop'
    bl_label = 'Stop'

    def execute(self, context):
        make.stop_project()
        return{'FINISHED'}

class ArmoryBuildButton(bpy.types.Operator):
    '''Build and compile project'''
    bl_idname = 'arm.build'
    bl_label = 'Build'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        make_renderer.check_default()

        state.target = make.runtime_to_target(in_viewport=False)
        state.is_export = False
        assets.invalidate_enabled = False
        make.build_project()
        make.compile_project(watch=True)
        assets.invalidate_enabled = True
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

        make_renderer.check_default()

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
        state.target = item.arm_project_target
        state.is_export = True
        assets.invalidate_shader_cache(None, None)
        assets.invalidate_enabled = False
        make.build_project()
        make.compile_project(watch=True)
        state.is_export = False
        wrd.arm_rplist_index = rplist_index
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryPatchProjectButton(bpy.types.Operator):
    '''
    Build/compile project without generating project files.
    This allows iterating faster on native platforms since project file is not reloaded.
    '''
    bl_idname = 'arm.patch_project'
    bl_label = 'Patch'
    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        self.report({'INFO'}, 'Patching project, check console for details.')

        arm.utils.check_projectpath(self)

        make_renderer.check_default()

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

        #make.clean_project()
        state.target = item.arm_project_target
        state.is_export = True
        assets.invalidate_enabled = False
        make.build_project(is_publish=True)
        make.compile_project(no_project_file=True)
        state.is_export = False
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

        make_renderer.check_default()

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

        make.clean_project()
        state.target = item.arm_project_target
        state.is_export = True
        assets.invalidate_enabled = False
        make.build_project(is_publish=True)
        make.compile_project(watch=True)
        state.is_export = False
        wrd.arm_rplist_index = rplist_index
        assets.invalidate_enabled = True
        target_name = make_utils.get_kha_target(state.target)
        files_path = arm.utils.get_fp_build() + '/' + target_name
        if target_name == 'html5':
            print('HTML5 files are being exported to ' + files_path)
        elif target_name == 'ios' or target_name == 'osx': # TODO: to macos
            print('XCode project files are being exported to ' + files_path + '-build')
        elif target_name == 'windows':
            print('VisualStudio 2017 project files are being exported to ' + files_path + '-build')
        elif target_name == 'windowsapp':
            print('VisualStudio 2017 project files are being exported to ' + files_path + '-build')
        elif target_name == 'android-native':
            print('Android Studio project files are being exported to ' + files_path + '-build/' + arm.utils.safestr(wrd.arm_project_name))
        else:
            print('Makefiles are being exported to ' + files_path + '-build')
        return{'FINISHED'}

class ArmoryPatchButton(bpy.types.Operator):
    '''Update currently running player instance'''
    bl_idname = 'arm.patch'
    bl_label = 'Patch'

    def execute(self, context):
        assets.invalidate_enabled = False
        make.play_project(True)
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

        make_utils.kode_studio()
        return{'FINISHED'}

class CleanMenu(bpy.types.Menu):
    bl_label = "Ok?"
    bl_idname = "OBJECT_MT_clean_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("arm.clean_cache")
        layout.operator("arm.clean_project")

class CleanButtonMenu(bpy.types.Operator):
    '''Clean cached data'''
    bl_label = "Clean"
    bl_idname = "arm.clean_menu"

    def execute(self, context):
        bpy.ops.wm.call_menu(name=CleanMenu.bl_idname)
        return {"FINISHED"}

class ArmoryCleanCacheButton(bpy.types.Operator):
    '''Delete all compiled data'''
    bl_idname = 'arm.clean_cache'
    bl_label = 'Clean Cache'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        make.clean_cache()
        return{'FINISHED'}

class ArmoryCleanProjectButton(bpy.types.Operator):
    '''Delete all cached project data'''
    bl_idname = 'arm.clean_project'
    bl_label = 'Clean Project'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        make.clean_project()
        return{'FINISHED'}

class ArmoryRenderButton(bpy.types.Operator):
    '''Capture Armory output as render result'''
    bl_idname = 'arm.render'
    bl_label = 'Render'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        make_renderer.check_default()

        if state.playproc != None:
            make.stop_project()
        if bpy.data.worlds['Arm'].arm_play_runtime != 'Krom':
            bpy.data.worlds['Arm'].arm_play_runtime = 'Krom'
        rpdat = arm.utils.get_rp()
        if rpdat.rp_rendercapture == False:
            rpdat.rp_rendercapture = True
        if rpdat.rp_antialiasing != 'TAA':
            rpdat.rp_antialiasing = 'TAA'
        assets.invalidate_enabled = False
        make.get_render_result()
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryRenderAnimButton(bpy.types.Operator):
    '''Capture Armory output as render result'''
    bl_idname = 'arm.render_anim'
    bl_label = 'Animation'

    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if not arm.utils.check_engine(self):
            return {"CANCELLED"}

        make_renderer.check_default()

        if state.playproc != None:
            make.stop_project()
        if bpy.data.worlds['Arm'].arm_play_runtime != 'Krom':
            bpy.data.worlds['Arm'].arm_play_runtime = 'Krom'
        rpdat = arm.utils.get_rp()
        if rpdat.rp_rendercapture == False:
            rpdat.rp_rendercapture = True
        if rpdat.rp_antialiasing != 'TAA':
            rpdat.rp_antialiasing = 'TAA'
        assets.invalidate_enabled = False
        make.get_render_anim_result()
        assets.invalidate_enabled = True
        return{'FINISHED'}

# Play button in 3D View panel
def draw_view3d_header(self, context):
    layout = self.layout
    if state.playproc == None and state.compileproc == None:
        if arm.utils.with_krom():
            layout.operator("arm.play_in_viewport", icon="PLAY")
        else:
            layout.operator("arm.play", icon="PLAY")
    else:
        layout.operator("arm.stop", icon="MESH_PLANE")

# Info panel in header
def draw_info_header(self, context):
    layout = self.layout
    if 'Arm' not in bpy.data.worlds:
        return
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_progress < 100:
        layout.prop(wrd, 'arm_progress')
    if log.info_text != '':
        layout.label(log.info_text)

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

        if wrd.arm_rplist_index >= 0 and len(wrd.arm_rplist) > 0:
            rpdat = wrd.arm_rplist[wrd.arm_rplist_index]
            layout.prop(wrd, "rp_preset")
            layout.separator()
            layout.prop(rpdat, "rp_renderer")
            layout.prop(rpdat, "arm_material_model")
            layout.prop(rpdat, "rp_shadowmap")
            if rpdat.rp_shadowmap != 'None':
                layout.prop(rpdat, "rp_shadowmap_cascades")
            layout.prop(rpdat, "rp_translucency_state")
            layout.prop(rpdat, "rp_overlays_state")
            layout.prop(rpdat, "rp_decals_state")
            layout.prop(rpdat, "rp_sss_state")
            layout.prop(rpdat, "rp_blending_state")
            layout.prop(rpdat, "rp_background")
            layout.prop(rpdat, 'rp_gi')
            if rpdat.rp_gi != 'Off':
                layout.prop(rpdat, 'rp_voxelgi_resolution')
                layout.prop(rpdat, 'rp_voxelgi_resolution_z')
                layout.prop(rpdat, 'arm_voxelgi_dimensions')
                layout.prop(rpdat, 'arm_voxelgi_revoxelize')
                if rpdat.arm_voxelgi_revoxelize:
                    layout.prop(rpdat, 'arm_voxelgi_camera')
                # layout.prop(rpdat, 'arm_voxelgi_anisotropic')
                layout.prop(rpdat, 'arm_voxelgi_shadows')
                if rpdat.rp_gi == 'Voxel GI':
                    layout.prop(rpdat, 'arm_voxelgi_refraction')
                    layout.prop(rpdat, 'arm_voxelgi_emission')
                    layout.prop(rpdat, 'rp_voxelgi_hdr')
                    # layout.prop(rpdat, 'arm_voxelgi_multibounce')
                layout.separator()

            layout.prop(rpdat, "rp_hdr")
            layout.prop(rpdat, "rp_stereo")
            layout.prop(rpdat, "rp_greasepencil")

            layout.separator()
            layout.prop(rpdat, "rp_render_to_texture")
            if rpdat.rp_render_to_texture:
                layout.prop(rpdat, "rp_supersampling")
                layout.prop(rpdat, "rp_antialiasing")
                layout.prop(rpdat, "rp_compositornodes")
                layout.prop(rpdat, "rp_volumetriclight")
                layout.prop(rpdat, "rp_ssao")
                layout.prop(rpdat, "rp_ssr")
                if rpdat.rp_ssr:
                    layout.prop(rpdat, 'arm_ssr_half_res')
                # layout.prop(wrd, 'arm_ssao_half_res')
                # layout.prop(rpdat, "rp_dfao")
                # layout.prop(rpdat, "rp_dfrs")
                # layout.prop(rpdat, "rp_dfgi")
                layout.prop(rpdat, "rp_bloom")
                layout.prop(rpdat, "rp_ocean")
                # layout.prop(rpdat, "rp_eyeadapt")
                layout.prop(rpdat, "rp_motionblur")
                layout.prop(rpdat, 'arm_rp_resolution')

            layout.separator()
            layout.prop(rpdat, 'arm_pcss_state')
            layout.prop(rpdat, 'arm_samples_per_pixel')
            layout.prop(rpdat, 'arm_texture_filter')
            layout.prop(rpdat, "arm_diffuse_model")
            layout.prop(rpdat, 'arm_ssrs')
            layout.prop(rpdat, 'arm_tessellation')
            layout.prop(rpdat, 'arm_clouds')

class ArmRenderPropsPanel(bpy.types.Panel):
    bl_label = "Armory Render Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']
        dat = bpy.data.worlds['Arm']

        layout.prop(wrd, 'arm_tonemap')
        layout.prop(wrd, 'arm_culling')
        layout.prop(wrd, 'arm_two_sided_area_lamp')
        layout.prop(wrd, 'arm_skin')
        if wrd.arm_skin.startswith('GPU'):
            layout.prop(wrd, 'arm_skin_max_bones_auto')
            if not wrd.arm_skin_max_bones_auto:
                layout.prop(wrd, 'arm_skin_max_bones')

        layout.label('PCSS')
        layout.prop(wrd, 'arm_pcss_rings')

        layout.label('Clouds')
        row = layout.row()
        row.prop(wrd, 'arm_clouds_density')
        row.prop(wrd, 'arm_clouds_size')
        row = layout.row()
        row.prop(wrd, 'arm_clouds_lower')
        row.prop(wrd, 'arm_clouds_upper')
        layout.prop(wrd, 'arm_clouds_wind')
        layout.prop(wrd, 'arm_clouds_secondary')
        row = layout.row()
        row.prop(wrd, 'arm_clouds_precipitation')
        row.prop(wrd, 'arm_clouds_eccentricity')

        layout.label('Voxel GI')
        row = layout.row()
        row.prop(wrd, 'arm_voxelgi_diff')
        row.prop(wrd, 'arm_voxelgi_spec')
        row = layout.row()
        row.prop(wrd, 'arm_voxelgi_occ')
        row.prop(wrd, 'arm_voxelgi_env')
        row = layout.row()
        row.prop(wrd, 'arm_voxelgi_step')
        row.prop(wrd, 'arm_voxelgi_range')
        row = layout.row()
        row.prop(wrd, 'arm_voxelgi_offset_diff')
        row.prop(wrd, 'arm_voxelgi_offset_spec')
        row = layout.row()
        row.prop(wrd, 'arm_voxelgi_offset_shadow')
        row.prop(wrd, 'arm_voxelgi_offset_refract')
        layout.prop(wrd, 'arm_voxelgi_diff_cones')

        layout.label('SSAO')
        row = layout.row()
        row.prop(wrd, 'arm_ssao_size')
        row.prop(wrd, 'arm_ssao_strength')

        layout.label('Bloom')
        row = layout.row()
        row.prop(wrd, 'arm_bloom_threshold')
        row.prop(wrd, 'arm_bloom_strength')
        layout.prop(wrd, 'arm_bloom_radius')

        layout.label('Motion Blur')
        layout.prop(wrd, 'arm_motion_blur_intensity')

        layout.label('SSR')
        row = layout.row()
        row.prop(wrd, 'arm_ssr_ray_step')
        row.prop(wrd, 'arm_ssr_min_ray_step')
        row = layout.row()
        row.prop(wrd, 'arm_ssr_search_dist')
        row.prop(wrd, 'arm_ssr_falloff_exp')
        layout.prop(wrd, 'arm_ssr_jitter')

        layout.label('SSS')
        layout.prop(wrd, 'arm_sss_width')

        layout.label('SSRS')
        layout.prop(wrd, 'arm_ssrs_ray_step')

        layout.label('Volumetric Light')
        layout.prop(wrd, 'arm_volumetric_light_air_turbidity')
        layout.prop(wrd, 'arm_volumetric_light_air_color')

        layout.label('Compositor')
        layout.prop(wrd, 'arm_letterbox')
        layout.prop(wrd, 'arm_letterbox_size')
        layout.prop(wrd, 'arm_grain')
        layout.prop(wrd, 'arm_grain_strength')
        layout.prop(wrd, 'arm_fog')
        layout.prop(wrd, 'arm_fog_color')
        row = layout.row()
        row.prop(wrd, 'arm_fog_amounta')
        row.prop(wrd, 'arm_fog_amountb')
        layout.prop(wrd, 'arm_fisheye')
        layout.prop(wrd, 'arm_vignette')
        layout.prop(wrd, 'arm_lens_texture')

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
            row.prop_search(item, "name", bpy.data, "objects", "Object")
            row = layout.row()
            row.prop(item, "screen_size_prop")

        # Auto lod for meshes
        if obj.type == 'MESH':
            layout.separator()
            layout.operator("arm.generate_lod")
            wrd = bpy.data.worlds['Arm']
            row = layout.row()
            row.prop(wrd, 'arm_lod_gen_levels')
            row.prop(wrd, 'arm_lod_gen_ratio')

        layout.prop(mdata, "arm_lod_material")

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

            layout.label('Actions')
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
            layout.label("Sync")
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
            self.report({'ERROR'}, 'Select linked object.')
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
    bpy.utils.register_class(WorldPropsPanel)
    bpy.utils.register_class(ArmoryPlayerPanel)
    bpy.utils.register_class(ArmoryRenderPanel)
    bpy.utils.register_class(ArmoryExporterPanel)
    bpy.utils.register_class(ArmoryProjectPanel)
    bpy.utils.register_class(ArmRenderPathPanel)
    bpy.utils.register_class(ArmRenderPropsPanel)
    # bpy.utils.register_class(ArmVirtualInputPanel)
    # bpy.utils.register_class(ArmGlobalVarsPanel)
    bpy.utils.register_class(ArmoryPlayButton)
    bpy.utils.register_class(ArmoryPlayInViewportButton)
    bpy.utils.register_class(ArmoryStopButton)
    bpy.utils.register_class(ArmoryBuildButton)
    bpy.utils.register_class(ArmoryBuildProjectButton)
    bpy.utils.register_class(ArmoryPatchProjectButton)
    bpy.utils.register_class(ArmoryPatchButton)
    bpy.utils.register_class(ArmoryOpenProjectFolderButton)
    bpy.utils.register_class(ArmoryKodeStudioButton)
    bpy.utils.register_class(CleanMenu)
    bpy.utils.register_class(CleanButtonMenu)
    bpy.utils.register_class(ArmoryCleanCacheButton)
    bpy.utils.register_class(ArmoryCleanProjectButton)
    bpy.utils.register_class(ArmoryPublishProjectButton)
    bpy.utils.register_class(ArmoryRenderButton)
    bpy.utils.register_class(ArmoryRenderAnimButton)
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

    bpy.types.VIEW3D_HT_header.append(draw_view3d_header)
    bpy.types.INFO_HT_header.prepend(draw_info_header)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)
    bpy.types.INFO_HT_header.remove(draw_info_header)

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
    bpy.utils.unregister_class(WorldPropsPanel)
    bpy.utils.unregister_class(ArmoryPlayerPanel)
    bpy.utils.unregister_class(ArmoryRenderPanel)
    bpy.utils.unregister_class(ArmoryExporterPanel)
    bpy.utils.unregister_class(ArmoryProjectPanel)
    bpy.utils.unregister_class(ArmRenderPathPanel)
    bpy.utils.unregister_class(ArmRenderPropsPanel)
    # bpy.utils.unregister_class(ArmVirtualInputPanel)
    # bpy.utils.unregister_class(ArmGlobalVarsPanel)
    bpy.utils.unregister_class(ArmoryPlayButton)
    bpy.utils.unregister_class(ArmoryPlayInViewportButton)
    bpy.utils.unregister_class(ArmoryStopButton)
    bpy.utils.unregister_class(ArmoryBuildButton)
    bpy.utils.unregister_class(ArmoryBuildProjectButton)
    bpy.utils.unregister_class(ArmoryPatchProjectButton)
    bpy.utils.unregister_class(ArmoryPatchButton)
    bpy.utils.unregister_class(ArmoryOpenProjectFolderButton)
    bpy.utils.unregister_class(ArmoryKodeStudioButton)
    bpy.utils.unregister_class(CleanMenu)
    bpy.utils.unregister_class(CleanButtonMenu)
    bpy.utils.unregister_class(ArmoryCleanCacheButton)
    bpy.utils.unregister_class(ArmoryCleanProjectButton)
    bpy.utils.unregister_class(ArmoryPublishProjectButton)
    bpy.utils.unregister_class(ArmoryRenderButton)
    bpy.utils.unregister_class(ArmoryRenderAnimButton)
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
