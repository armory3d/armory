import bpy
import armutils
import make
import make_state as state
import space_armory
import time
import bridge
import log
try:
    import barmory
except ImportError:
    pass

last_time = time.time()
last_operator = None

def on_scene_update_post(context):
    global last_time
    global last_operator

    if time.time() - last_time >= (1 / bpy.context.scene.render.fps): # Use frame rate for update frequency for now
        last_time = time.time()

        # Tag redraw if playing in space_armory
        state.last_chromium_running = state.chromium_running
        state.chromium_running = False
        if not state.is_paused:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_ARMORY':
                    state.chromium_running = True
                    barmory.draw()

        # Have to update chromium one more time before exit, to prevent 'AudioSyncReader::Read timed out' warnings
        if state.chromium_running == False:
            if state.last_chromium_running:
                barmory.draw()

        # Auto patch on every operator change
        ops = bpy.context.window_manager.operators
        if state.chromium_running and \
           bpy.data.worlds['Arm'].arm_play_live_patch and \
           bpy.data.worlds['Arm'].arm_play_auto_build and \
           len(ops) > 0 and \
           last_operator != ops[-1]:
            last_operator = ops[-1]
            # Othwerwise rebuild scene
            if bridge.send_operator(last_operator) == False:
                make.patch_project()
                make.compile_project()

        # Check if chromium is running
        if armutils.with_chromium():
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_ARMORY':
                    # Read chromium console
                    if barmory.get_console_updated() == 1:
                        log.print_player(barmory.get_console())
                        area.tag_redraw()
                    # Read operator console
                    if barmory.get_operator_updated() == 1:
                        bridge.parse_operator(barmory.get_operator())
                    break

        # New output has been logged
        if log.tag_redraw:
            log.tag_redraw = False
            for area in bpy.context.screen.areas:
                if area.type == 'INFO':
                    area.tag_redraw()
                    break

        # Player finished, redraw play buttons
        if state.playproc_finished:
            state.playproc_finished = False
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                    area.tag_redraw()

        # Compilation finished
        if state.compileproc_finished:
            state.compileproc_finished = False
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                    area.tag_redraw()
            # Compilation succesfull
            if state.compileproc_success:
                # Notify embedded player
                if state.chromium_running:
                    barmory.call_js('armory.Scene.patch();')
                # Or switch to armory space
                elif armutils.with_chromium() and state.in_viewport:
                    state.play_area.type = 'VIEW_ARMORY'
                    # Prevent immediate operator patch
                    if len(ops) > 0:
                        last_operator = ops[-1]

    edit_obj = bpy.context.edit_object
    if edit_obj != None and edit_obj.is_updated_data:
        if edit_obj.type == 'MESH':
            edit_obj.data.mesh_cached = False
        elif edit_obj.type == 'ARMATURE':
            edit_obj.data.data_cached = False

def on_load_pre(context):
    bpy.ops.arm_addon.stop('EXEC_DEFAULT')

def register():
    bpy.app.handlers.scene_update_post.append(on_scene_update_post)
    bpy.app.handlers.load_pre.append(on_load_pre)

def unregister():
    bpy.app.handlers.scene_update_post.remove(on_scene_update_post)
    bpy.app.handlers.load_pre.remove(on_load_pre)
