import bpy
import armutils
import make
import make_state as state
import space_armory
import nodes_renderpath
import time
import bridge
import log
import props
from bpy.app.handlers import persistent
try:
    import barmory
except ImportError:
    pass

last_time = time.time()
# last_update_time = time.time()
last_operator = None
redraw_ui = False
redraw_progress = False

@persistent
def on_scene_update_post(context):
    global last_time
    # global last_update_time
    global last_operator
    global redraw_ui
    global redraw_progress

    # Redraw at the start of 'next' frame
    if redraw_ui and bpy.context.screen != None:
        for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                    area.tag_redraw()
        redraw_ui = False
    if redraw_progress and bpy.context.screen != None:
        for area in bpy.context.screen.areas:
            if area.type == 'INFO':
                area.tag_redraw()
                break
        redraw_progress = False

    # New operator
    ops = bpy.context.window_manager.operators
    operators_changed = False
    if len(ops) > 0 and last_operator != ops[-1]:
        last_operator = ops[-1]
        operators_changed = True

    # Player running
    state.krom_running = False
    if not state.is_paused and bpy.context.screen != None:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_ARMORY':
                state.krom_running = True
                break

    # Auto patch on every operator change
    if state.krom_running and \
       bpy.data.worlds['Arm'].arm_play_live_patch and \
       bpy.data.worlds['Arm'].arm_play_auto_build and \
       operators_changed:
        # Otherwise rebuild scene
        if bridge.send_operator(last_operator) == False:
            make.patch_project()
            make.compile_project(target_name="krom", patch=True)

    # Use frame rate for update frequency for now
    if time.time() - last_time >= (1 / bpy.context.scene.render.fps):
        last_time = time.time()

        if state.krom_running:
            # Read krom console
            if barmory.get_console_updated() == 1:
                log.print_player(barmory.get_console())
            # Read operator console
            if barmory.get_operator_updated() == 1:
                bridge.parse_operator(barmory.get_operator())
            # Tag redraw
            if bpy.context.screen != None:
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_ARMORY':
                        area.tag_redraw()
                        break

        # New output has been logged
        if log.tag_redraw and bpy.context.screen != None:
            log.tag_redraw = False
            redraw_progress = True

        # Player finished, redraw play buttons
        if state.playproc_finished and bpy.context.screen != None:
            state.playproc_finished = False
            redraw_ui = True

        # Compilation finished
        if state.compileproc_finished and bpy.context.screen != None:
            state.compileproc_finished = False
            redraw_ui = True
            # Compilation succesfull
            if state.compileproc_success:
                # Notify embedded player
                if state.krom_running:
                    barmory.call_js('armory.Scene.patch();')
                # Or switch to armory space
                elif armutils.with_krom() and state.in_viewport:
                    state.play_area.type = 'VIEW_ARMORY'
                    # Prevent immediate operator patch
                    if len(ops) > 0:
                        last_operator = ops[-1]

    # No attribute when using multiple windows?
    if hasattr(bpy.context, 'edit_object'):
        edit_obj = bpy.context.edit_object
        if edit_obj != None and edit_obj.is_updated_data:
            if edit_obj.type == 'MESH':
                edit_obj.data.mesh_cached = False
            elif edit_obj.type == 'ARMATURE':
                edit_obj.data.data_cached = False

    if hasattr(bpy.context, 'object'):
        obj = bpy.context.object
        if obj != None:
            if operators_changed:
                # Modifier was added/removed, recache mesh
                if ops[-1].bl_idname == 'OBJECT_OT_modifier_add' or ops[-1].bl_idname == 'OBJECT_OT_modifier_remove':
                    obj.data.mesh_cached = False
            if obj.active_material != None and obj.active_material.is_updated:
                obj.active_material.is_cached = False

@persistent
def on_load_post(context):
    props.init_properties_on_load()
    nodes_renderpath.reload_blend_data()

@persistent
def on_save_pre(context):
    props.init_properties_on_save()

def register():
    bpy.app.handlers.scene_update_post.append(on_scene_update_post)
    bpy.app.handlers.save_pre.append(on_save_pre)
    bpy.app.handlers.load_post.append(on_load_post)

def unregister():
    bpy.app.handlers.scene_update_post.remove(on_scene_update_post)
    bpy.app.handlers.save_pre.remove(on_save_pre)
    bpy.app.handlers.load_post.remove(on_load_post)
