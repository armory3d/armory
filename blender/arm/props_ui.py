import bpy
import subprocess
import webbrowser
from bpy.types import Menu, Panel, UIList
from bpy.props import *
from arm.props_traits_clip import *
from arm.props_traits_action import *
import arm.utils
import arm.make_renderer as make_renderer
import arm.make as make
import arm.make_utils as make_utils
import arm.make_state as state
import arm.assets as assets
import arm.log as log

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
            
        wrd = bpy.data.worlds['Arm']

        if wrd.arm_export_hide_render == False:
            layout.prop(obj, 'hide_render')
            hide = obj.hide_render
        else:
            layout.prop(obj, 'game_export')
            hide = not obj.game_export
        
        if hide:
            return
        
        layout.prop(wrd, 'arm_object_advanced')
        if wrd.arm_object_advanced:
            if wrd.arm_export_hide_render == False:
                layout.prop(obj, 'game_visible')
            else:
                layout.prop(obj, 'hide_render')
            row = layout.row(align=True)
            row.prop(obj, 'spawn')
            row.prop(obj, 'mobile')
            if obj.type == 'MESH':
                layout.prop(obj, 'instanced_children')
                if obj.instanced_children:
                    layout.label('Location')
                    row = layout.row()
                    row.prop(obj, 'instanced_children_loc_x')
                    row.prop(obj, 'instanced_children_loc_y')
                    row.prop(obj, 'instanced_children_loc_z')
                    layout.label('Rotation')
                    row = layout.row()
                    row.prop(obj, 'instanced_children_rot_x')
                    row.prop(obj, 'instanced_children_rot_y')
                    row.prop(obj, 'instanced_children_rot_z')
                    layout.label('Scale')
                    row = layout.row()
                    row.prop(obj, 'instanced_children_scale_x')
                    row.prop(obj, 'instanced_children_scale_y')
                    row.prop(obj, 'instanced_children_scale_z')
                layout.prop(obj, 'override_material')
                if obj.override_material:
                    layout.prop(obj, 'override_material_name')

            if obj.type == 'ARMATURE':
                layout.prop(obj, 'bone_animation_enabled')
                if obj.bone_animation_enabled:
                    layout.prop(obj, 'edit_actions_prop')
                    if obj.edit_actions_prop:
                        layout.prop_search(obj, "start_action_name_prop", obj.data, "my_actiontraitlist", "Start Action")
            else:
                layout.prop(obj, 'object_animation_enabled')
            
            if (obj.type == 'ARMATURE' and obj.bone_animation_enabled) or (obj.type != 'ARMATURE' and obj.object_animation_enabled):
                layout.prop(obj, 'edit_tracks_prop')
                if obj.edit_tracks_prop:
                    layout.prop_search(obj, "start_track_name_prop", obj, "my_cliptraitlist", "Start Clip")
                    # Tracks list
                    layout.label("Clips")
                    animrow = layout.row()
                    animrows = 2
                    if len(obj.my_cliptraitlist) > 1:
                        animrows = 4
                    
                    row = layout.row()
                    row.template_list("MY_UL_ClipTraitList", "The_List", obj, "my_cliptraitlist", obj, "cliptraitlist_index", rows=animrows)

                    col = row.column(align=True)
                    col.operator("my_cliptraitlist.new_item", icon='ZOOMIN', text="")
                    col.operator("my_cliptraitlist.delete_item", icon='ZOOMOUT', text="")

                    if len(obj.my_cliptraitlist) > 1:
                        col.separator()
                        col.operator("my_cliptraitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
                        col.operator("my_cliptraitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

                    if obj.cliptraitlist_index >= 0 and len(obj.my_cliptraitlist) > 0:
                        animitem = obj.my_cliptraitlist[obj.cliptraitlist_index]         
                        row = layout.row()
                        row.prop(animitem, "start_prop")
                        row.prop(animitem, "end_prop")
                        layout.prop(animitem, "speed_prop")
                        row = layout.row(align=True)
                        row.prop(animitem, "loop_prop")
                        row.prop(animitem, "reflect_prop")

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
            layout.prop(bpy.data.worlds['Arm'], 'generate_ocean_base_color')
            layout.prop(bpy.data.worlds['Arm'], 'generate_ocean_water_color')
            layout.prop(bpy.data.worlds['Arm'], 'generate_ocean_fade')

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

        layout.prop(obj, 'soft_body_margin')

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

        if obj.type == 'CAMERA':
            layout.prop(obj.data, 'is_probe')
            if obj.data.is_probe == True:
                layout.prop(obj.data, 'probe_texture')
                layout.prop_search(obj.data, "probe_volume", bpy.data, "objects")
                layout.prop(obj.data, 'probe_strength')
                layout.prop(obj.data, 'probe_blending')
            layout.prop(obj.data, 'is_mirror')
            if obj.data.is_mirror == True:
                layout.label('Resolution')
                row = layout.row(align=True)
                row.prop(obj.data, 'mirror_resolution_x')
                row.prop(obj.data, 'mirror_resolution_y')
            layout.prop(obj.data, 'frustum_culling')
            layout.prop_search(obj.data, "renderpath_path", bpy.data, "node_groups")
        elif obj.type == 'MESH' or obj.type == 'FONT' or obj.type == 'META':
            row = layout.row(align=True)
            row.prop(obj.data, 'dynamic_usage')
            row.prop(obj.data, 'data_compressed')
            if obj.type == 'MESH':
                layout.prop(obj.data, 'sdfgen')
            layout.operator("arm.invalidate_cache")
        elif obj.type == 'LAMP':
            row = layout.row(align=True)
            row.prop(obj.data, 'lamp_clip_start')
            row.prop(obj.data, 'lamp_clip_end')
            row = layout.row(align=False)
            row.prop(obj.data, 'lamp_fov')
            row.prop(obj.data, 'lamp_shadows_bias')
            if obj.data.type == 'POINT':
                layout.prop(obj.data, 'lamp_omni_shadows')
                if obj.data.lamp_omni_shadows:
                    layout.prop(obj.data, 'lamp_omni_shadows_cubemap')
                    if not obj.data.lamp_omni_shadows_cubemap:
                        layout.label('Warning: Will result in performance loss')
                    else:
                        layout.prop(bpy.data.worlds['Arm'], 'lamp_omni_shadows_cubemap_pcfsize')
        elif obj.type == 'SPEAKER':
            layout.prop(obj.data, 'loop')
            layout.prop(obj.data, 'stream')
        elif obj.type == 'ARMATURE':
            layout.prop(obj.data, 'edit_actions')
            if obj.data.edit_actions:
                # Actions list
                layout.label("Actions")
                animrow = layout.row()
                animrows = 2
                if len(obj.data.my_actiontraitlist) > 1:
                    animrows = 4
                
                row = layout.row()
                row.template_list("MY_UL_ActionTraitList", "The_List", obj.data, "my_actiontraitlist", obj.data, "actiontraitlist_index", rows=animrows)

                col = row.column(align=True)
                col.operator("my_actiontraitlist.new_item", icon='ZOOMIN', text="")
                col.operator("my_actiontraitlist.delete_item", icon='ZOOMOUT', text="")

                if len(obj.data.my_actiontraitlist) > 1:
                    col.separator()
                    col.operator("my_actiontraitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("my_actiontraitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

                if obj.data.actiontraitlist_index >= 0 and len(obj.data.my_actiontraitlist) > 0:
                    item = obj.data.my_actiontraitlist[obj.data.actiontraitlist_index]
                    item.name = item.action_name_prop
                    row = layout.row()
                    row.prop_search(item, "action_name_prop", bpy.data, "actions", "Action")

            layout.prop(obj.data, 'data_compressed')

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
        layout.prop(scene, 'game_export')
        layout.prop(scene, 'gp_export')
        if scene.gp_export:
            layout.operator('arm.invalidate_gp_cache')
        layout.prop(scene, 'data_compressed')

class InvalidateCacheButton(bpy.types.Operator):
    '''Delete cached mesh data'''
    bl_idname = "arm.invalidate_cache"
    bl_label = "Invalidate Cache"
 
    def execute(self, context):
        context.object.data.mesh_cached = False
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
    bl_label = "Invalidate Grease Pencil Cache"
 
    def execute(self, context):
        if context.scene.grease_pencil != None:
            context.scene.grease_pencil.data_cached = False
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

        row = layout.row(align=True)
        row.prop(mat, 'cast_shadow')
        row.prop(mat, 'receive_shadow')
        
        layout.prop(bpy.data.worlds['Arm'], 'arm_material_advanced')
        if bpy.data.worlds['Arm'].arm_material_advanced:
            layout.prop(mat, 'overlay')
            layout.prop(mat, 'decal')
            layout.prop(mat, 'override_cull')
            if mat.override_cull:
                layout.prop(mat, 'override_cull_mode')
            layout.prop(mat, 'override_shader')
            if mat.override_shader:
                layout.prop(mat, 'override_shader_name')
            layout.prop(mat, 'override_shader_context')
            if mat.override_shader_context:
                layout.prop(mat, 'override_shader_context_name')
            # layout.prop(mat, 'override_compare')
            # if mat.override_compare:
                # layout.prop(mat, 'override_compare_mode')
            # layout.prop(mat, 'override_depthwrite')
            # if mat.override_depthwrite:
                # layout.prop(mat, 'override_depthwrite_mode')
            layout.prop(mat, 'stencil_mask')
            layout.prop(mat, 'skip_context')
            layout.label('Height map')
            layout.prop(mat, 'height_tess')
            if mat.height_tess:
                row = layout.row(align=True)
                row.prop(mat, 'height_tess_inner')
                row.prop(mat, 'height_tess_outer')
            layout.prop(mat, 'height_tess_shadows')
            if mat.height_tess_shadows:
                row = layout.row(align=True)
                row.prop(mat, 'height_tess_shadows_inner')
                row.prop(mat, 'height_tess_shadows_outer')
            layout.prop(mat, 'transluc_shadows')

            layout.operator("arm.invalidate_material_cache")

class WorldPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
 
    def draw(self, context):
        layout = self.layout
        # wrd = bpy.context.world
        wrd = bpy.data.worlds['Arm']
        
        row = layout.row(align=True)
        row.prop(wrd, 'generate_irradiance')
        if wrd.generate_irradiance:
            row.prop(wrd, 'generate_radiance')
            if wrd.generate_radiance:
                layout.prop(wrd, 'generate_radiance_size')

                layout.prop(wrd, 'generate_radiance_sky')
                if wrd.generate_radiance_sky:
                    layout.prop(wrd, 'generate_radiance_sky_type')

        layout.separator()
        # TODO: migrate to compositor
        layout.label('Compositor (deprecated)')
        layout.prop(wrd, 'generate_tonemap')
        layout.prop(wrd, 'generate_letterbox')
        if wrd.generate_letterbox:
            layout.prop(wrd, 'generate_letterbox_size')
        layout.prop(wrd, 'generate_grain')
        if wrd.generate_grain:
            layout.prop(wrd, 'generate_grain_strength')
        layout.prop(wrd, 'generate_fog')
        if wrd.generate_fog:
            layout.prop(wrd, 'generate_fog_color')
            layout.prop(wrd, 'generate_fog_amounta')
            layout.prop(wrd, 'generate_fog_amountb')
        layout.prop(wrd, 'generate_fisheye')
        layout.prop(wrd, 'generate_vignette')
        layout.prop(wrd, 'generate_lamp_texture')
        layout.prop(wrd, 'generate_lens_texture')
        layout.prop(wrd, 'generate_lamp_falloff')

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
        layout.prop(wrd, 'arm_play_viewport_camera')
        if wrd.arm_play_viewport_camera:
            layout.prop(wrd, 'arm_play_viewport_navigation')

        layout.prop(wrd, 'arm_play_advanced')
        if wrd.arm_play_advanced:
            layout.prop(wrd, make_utils.runtime_to_gapi())
            layout.prop(wrd, 'arm_play_console')
            if arm.utils.with_krom():
                row = layout.row(align=True)
                row.prop(wrd, 'arm_play_live_patch')
                if wrd.arm_play_live_patch:
                    row.prop(wrd, 'arm_play_auto_build')
            layout.operator("arm.render", icon="RENDER_STILL")

            row = layout.row(align=True)
            row.prop(wrd, 'arm_cache_shaders')
            row.prop(wrd, 'arm_cache_compiler')
            row = layout.row(align=True)
            row.prop(wrd, 'arm_minimize')
            row.prop(wrd, 'arm_optimize_mesh')
            row = layout.row(align=True)
            row.prop(wrd, 'arm_gpu_processing')
            row.prop(wrd, 'arm_sampled_animation')
            row = layout.row(align=True)
            row.prop(wrd, 'arm_batch_meshes')
            row.prop(wrd, 'arm_batch_materials')
            row = layout.row(align=True)
            row.prop(wrd, 'arm_deinterleaved_buffers')
            row.prop(wrd, 'arm_export_tangents')
            layout.prop(wrd, 'arm_stream_scene')
            layout.label('Libraries')
            layout.prop(wrd, 'arm_physics')
            layout.prop(wrd, 'arm_navigation')
            layout.prop(wrd, 'arm_ui')
            layout.prop(wrd, 'arm_hscript')

class ArmoryProjectPanel(bpy.types.Panel):
    bl_label = "Armory Project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']
        layout.prop(wrd, 'arm_project_name')
        layout.prop(wrd, 'arm_project_package')
        layout.prop_search(wrd, 'arm_khafile', bpy.data, 'texts', 'Khafile')
        layout.prop_search(wrd, 'arm_khamake', bpy.data, 'texts', 'Khamake')
        row = layout.row(align=True)
        row.operator("arm.kode_studio")
        row.operator("arm.open_project_folder")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("arm.build_project")
        row.operator("arm.publish_project")
        layout.prop(wrd, 'arm_project_target')
        layout.prop(wrd, make_utils.target_to_gapi())
        layout.prop(wrd, 'arm_dce')

        layout.label("Libraries")
        rows = 2
        if len(wrd.my_librarytraitlist) > 1:
            rows = 4
        
        row = layout.row()
        row.template_list("MY_UL_LibraryTraitList", "The_List", wrd, "my_librarytraitlist", wrd, "librarytraitlist_index", rows=rows)

        col = row.column(align=True)
        col.operator("my_librarytraitlist.new_item", icon='ZOOMIN', text="")
        col.operator("my_librarytraitlist.delete_item", icon='ZOOMOUT', text="")

        if len(wrd.my_librarytraitlist) > 1:
            col.separator()
            col.operator("my_librarytraitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("my_librarytraitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

        # if wrd.librarytraitlist_index >= 0 and len(wrd.my_librarytraitlist) > 0:
            # libitem = wrd.my_librarytraitlist[wrd.librarytraitlist_index]         
            

        layout.prop(wrd, 'arm_project_advanced')
        if wrd.arm_project_advanced:
            row = layout.row()
            row.prop(wrd, 'arm_loadbar')
            row.prop(wrd, 'arm_vsync')
            row = layout.row()
            row.prop(wrd, 'arm_export_hide_render')
            row.prop(wrd, 'arm_spawn_all_layers')
            layout.prop(wrd, 'arm_play_active_scene')
            if wrd.arm_play_active_scene == False:
                layout.prop_search(wrd, 'arm_project_scene', bpy.data, 'scenes', 'Scene')
            layout.prop(wrd, 'arm_winmode')
            layout.label('Armory v' + wrd.arm_version)
            layout.operator('arm.check_updates')
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator('arm.open_manual')
            row.operator('arm.report_issue')

class ArmoryPlayButton(bpy.types.Operator):
    '''Launch player in new window'''
    bl_idname = 'arm.play'
    bl_label = 'Play'
 
    def execute(self, context):
        if state.compileproc != None:
            return {"CANCELLED"}
        
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_camera(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}
            
        make_renderer.check_default()

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

        if not arm.utils.check_camera(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        if context.area == None:
            return {"CANCELLED"}

        make_renderer.check_default()

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

        if not arm.utils.check_camera(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        state.target = make.runtime_to_target(in_viewport=False)
        assets.invalidate_enabled = False
        make.build_project(target=state.target)
        make.compile_project(target_name=state.target, watch=True)
        assets.invalidate_enabled = True
        return{'FINISHED'}

class ArmoryBuildProjectButton(bpy.types.Operator):
    '''Build and compile project'''
    bl_idname = 'arm.build_project'
    bl_label = 'Build'
 
    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_camera(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        state.target = bpy.data.worlds['Arm'].arm_project_target
        assets.invalidate_enabled = False
        make.build_project(target=state.target)
        make.compile_project(target_name=state.target, watch=True)
        assets.invalidate_enabled = True
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

class ArmoryCheckUpdatesButton(bpy.types.Operator):
    '''Open a website in the web-browser'''
    bl_idname = 'arm.check_updates'
    bl_label = 'Check for Updates'
 
    def execute(self, context):
        webbrowser.open("http://armory3d.org/download.html")
        return{'FINISHED'}

class ArmoryManualButton(bpy.types.Operator):
    '''Open a website in the web-browser'''
    bl_idname = 'arm.open_manual'
    bl_label = 'Manual'
 
    def execute(self, context):
        webbrowser.open("http://armory3d.org/manual/")
        return{'FINISHED'}

class ArmoryReportIssueButton(bpy.types.Operator):
    '''Open a website in the web-browser'''
    bl_idname = 'arm.report_issue'
    bl_label = 'Report Issue'
 
    def execute(self, context):
        webbrowser.open("https://github.com/armory3d/armory/issues")
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

class ArmoryPublishButton(bpy.types.Operator):
    '''Build project ready for publishing'''
    bl_idname = 'arm.publish_project'
    bl_label = 'Publish'
 
    def execute(self, context):
        if not arm.utils.check_saved(self):
            return {"CANCELLED"}

        if not arm.utils.check_camera(self):
            return {"CANCELLED"}

        if not arm.utils.check_sdkpath(self):
            return {"CANCELLED"}

        make.publish_project()
        self.report({'INFO'}, 'Publishing project, check console for details.')
        return{'FINISHED'}

class ArmoryRenderButton(bpy.types.Operator):
    '''Capture Armory output as render result'''
    bl_idname = 'arm.render'
    bl_label = 'Render'
 
    def execute(self, context):
        if state.playproc == None:
            self.report({"ERROR"}, "Run Armory player in electron window first")
            return {"CANCELLED"}
        make.get_render_result()
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
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_progress < 100:
        layout.prop(wrd, 'arm_progress')
    if log.info_text != '':
        layout.label(log.info_text)

def register():
    bpy.utils.register_class(ObjectPropsPanel)
    bpy.utils.register_class(ModifiersPropsPanel)
    bpy.utils.register_class(PhysicsPropsPanel)
    bpy.utils.register_class(DataPropsPanel)
    bpy.utils.register_class(ScenePropsPanel)
    bpy.utils.register_class(InvalidateCacheButton)
    bpy.utils.register_class(InvalidateMaterialCacheButton)
    bpy.utils.register_class(InvalidateGPCacheButton)
    bpy.utils.register_class(MaterialPropsPanel)
    bpy.utils.register_class(WorldPropsPanel)
    bpy.utils.register_class(ArmoryPlayerPanel)
    bpy.utils.register_class(ArmoryProjectPanel)
    bpy.utils.register_class(ArmoryPlayButton)
    bpy.utils.register_class(ArmoryPlayInViewportButton)
    bpy.utils.register_class(ArmoryStopButton)
    bpy.utils.register_class(ArmoryBuildButton)
    bpy.utils.register_class(ArmoryBuildProjectButton)
    bpy.utils.register_class(ArmoryPatchButton)
    bpy.utils.register_class(ArmoryOpenProjectFolderButton)
    bpy.utils.register_class(ArmoryCheckUpdatesButton)
    bpy.utils.register_class(ArmoryManualButton)
    bpy.utils.register_class(ArmoryReportIssueButton)
    bpy.utils.register_class(ArmoryKodeStudioButton)
    bpy.utils.register_class(CleanMenu)
    bpy.utils.register_class(CleanButtonMenu)
    bpy.utils.register_class(ArmoryCleanCacheButton)
    bpy.utils.register_class(ArmoryCleanProjectButton)
    bpy.utils.register_class(ArmoryPublishButton)
    bpy.utils.register_class(ArmoryRenderButton)

    bpy.types.VIEW3D_HT_header.append(draw_view3d_header)
    bpy.types.INFO_HT_header.prepend(draw_info_header)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)
    bpy.types.INFO_HT_header.remove(draw_info_header)

    bpy.utils.unregister_class(ObjectPropsPanel)
    bpy.utils.unregister_class(ModifiersPropsPanel)
    bpy.utils.unregister_class(PhysicsPropsPanel)
    bpy.utils.unregister_class(DataPropsPanel)
    bpy.utils.unregister_class(ScenePropsPanel)
    bpy.utils.unregister_class(InvalidateCacheButton)
    bpy.utils.unregister_class(InvalidateMaterialCacheButton)
    bpy.utils.unregister_class(InvalidateGPCacheButton)
    bpy.utils.unregister_class(MaterialPropsPanel)
    bpy.utils.unregister_class(WorldPropsPanel)
    bpy.utils.unregister_class(ArmoryPlayerPanel)
    bpy.utils.unregister_class(ArmoryProjectPanel)
    bpy.utils.unregister_class(ArmoryPlayButton)
    bpy.utils.unregister_class(ArmoryPlayInViewportButton)
    bpy.utils.unregister_class(ArmoryStopButton)
    bpy.utils.unregister_class(ArmoryBuildButton)
    bpy.utils.unregister_class(ArmoryBuildProjectButton)
    bpy.utils.unregister_class(ArmoryPatchButton)
    bpy.utils.unregister_class(ArmoryOpenProjectFolderButton)
    bpy.utils.unregister_class(ArmoryCheckUpdatesButton)
    bpy.utils.unregister_class(ArmoryManualButton)
    bpy.utils.unregister_class(ArmoryReportIssueButton)
    bpy.utils.unregister_class(ArmoryKodeStudioButton)
    bpy.utils.unregister_class(CleanMenu)
    bpy.utils.unregister_class(CleanButtonMenu)
    bpy.utils.unregister_class(ArmoryCleanCacheButton)
    bpy.utils.unregister_class(ArmoryCleanProjectButton)
    bpy.utils.unregister_class(ArmoryPublishButton)
    bpy.utils.unregister_class(ArmoryRenderButton)
