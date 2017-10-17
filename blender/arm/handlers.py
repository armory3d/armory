import bpy
import time
import os
import sys
from bpy.app.handlers import persistent
import arm.utils
import arm.bridge as bridge
import arm.log as log
import arm.props as props
import arm.make as make
import arm.make_state as state
import arm.space_armory as space_armory
import arm.make_renderer as make_renderer
import arm.assets as assets
try:
    import barmory
except ImportError:
    pass

last_time = time.time()
# last_update_time = time.time()
last_operator = None
redraw_ui = False
redraw_progress = False
first_update = True

@persistent
def on_scene_update_post(context):
    global last_time
    # global last_update_time
    global last_operator
    global redraw_ui
    global redraw_progress
    global first_update

    if first_update == True: # Skip first one, object reports is_update_data
        first_update = False
        return

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
    # Undo was performed - Blender clears the complete operator stack, undo last known operator atleast
    # if len(ops) == 0 and last_operator != None:
        # if hasattr(bpy.context, 'object'):
            # op_changed(last_operator, bpy.context.object)
        # last_operator = None

    if state.is_render_anim:
        pass
    elif state.is_render:
        import numpy
        # fp = arm.utils.get_fp_build()
        krom_location, krom_path = arm.utils.krom_paths()
        fp = krom_location
        resx, resy = arm.utils.get_render_resolution(arm.utils.get_active_scene())
        wrd = bpy.data.worlds['Arm']
        cformat = wrd.rp_rendercapture_format
        if cformat == '8bit':
            cbits = 4
            ctype = numpy.uint8
        elif cformat == '16bit':
            cbits = 8
            ctype = numpy.float16
        elif cformat == '32bit':
            cbits = 16
            ctype = numpy.float32
        if os.path.isfile(fp + '/render.bin') and os.path.getsize(fp + '/render.bin') == resx * resy * cbits:
            data = numpy.fromfile(fp + '/render.bin', dtype=ctype)
            data = data.astype(float)
            if cformat == '8bit':
                data = numpy.divide(data, 255)
            n = "Render Result"
            if n in bpy.data.images and bpy.data.images[n].size[0] == resx and bpy.data.images[n].size[1] == resy:
                bpy.data.images[n].pixels = data
            else:
                float_buffer = cformat != '8bit'
                image = bpy.data.images.new("Render Result", width=resx, height=resy, float_buffer=float_buffer)
                image.pixels = data
            state.is_render = False
            os.remove(fp + '/render.bin')
            print('Output image captured into Blender - UV/Image Editor - Render Result')

    # Player running
    state.krom_running = False
    if not state.is_paused and bpy.context.screen != None:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_ARMORY':
                state.krom_running = True
                break

    # Auto patch on every operator change
    if not 'Arm' in bpy.data.worlds:
        props.create_wrd()
    wrd = bpy.data.worlds['Arm']
    if state.krom_running and \
       wrd.arm_play_live_patch and \
       wrd.arm_play_auto_build and \
       operators_changed:
        # Otherwise rebuild scene
        if bridge.send_operator(last_operator) == False:
            if state.compileproc == None:
                # state.is_paused = True # Speeds up recompile
                assets.invalidate_enabled = False
                make.play_project(in_viewport=True)
                assets.invalidate_enabled = True

    # Update at 60 fps
    fps_mult = 2.0 if (state.krom_running and arm.utils.get_os() == 'win') else 1.0 # Handlers called less frequently on Windows?
    fps = 60
    if time.time() - last_time >= (1 / (fps * fps_mult)):
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
                    if state.recompiled and wrd.arm_play_live_patch:
                        # state.is_paused = False
                        barmory.parse_code()
                        for s in state.mod_scripts:
                            barmory.call_js('armory.Scene.patchTrait("' + s + '");')
                    else:
                        barmory.call_js('armory.Scene.patch();')
                # Or switch to armory space
                elif arm.utils.with_krom() and state.in_viewport:
                    state.play_area.type = 'VIEW_ARMORY'
                    # Prevent immediate operator patch
                    if len(ops) > 0:
                        last_operator = ops[-1]

    # No attribute when using multiple windows?
    if hasattr(bpy.context, 'active_object'):
        obj = bpy.context.active_object
        if obj != None:
            if obj.is_updated_data: # + data.is_updated
                recache(obj)
            if obj.type == 'ARMATURE': # Newly parented objects needs to be recached
                for c in obj.children:
                    if c.is_updated_data:
                        recache(c)
    if hasattr(bpy.context, 'sculpt_object') and bpy.context.sculpt_object != None:
        recache(bpy.context.sculpt_object)
    if hasattr(bpy.context, 'active_pose_bone') and bpy.context.active_pose_bone != None:
        recache(bpy.context.active_object)

    if hasattr(bpy.context, 'object'):
        obj = bpy.context.object
        if obj != None:
            if operators_changed:
                op_changed(ops[-1], obj)
            if obj.active_material != None and obj.active_material.is_updated:
                if obj.active_material.lock_cache == True: # is_cached was set to true
                    obj.active_material.lock_cache = False
                else:
                    obj.active_material.is_cached = False

    # Invalidate logic node tree cache if it is being edited..
    space = arm.utils.logic_editor_space()
    if space != None:
        space.node_tree.is_cached = False

def recache(edit_obj):
    if hasattr(edit_obj.data, 'arm_cached'):
        edit_obj.data.arm_cached = False

def op_changed(op, obj):
    # Recache mesh data
    if op.bl_idname == 'OBJECT_OT_modifier_add' or \
       op.bl_idname == 'OBJECT_OT_modifier_remove' or \
       op.bl_idname == 'OBJECT_OT_transform_apply' or \
       op.bl_idname == 'OBJECT_OT_shade_smooth' or \
       op.bl_idname == 'OBJECT_OT_shade_flat':
        obj.data.arm_cached = False

appended_py_paths = []
@persistent
def on_load_post(context):
    global appended_py_paths
    global first_update

    first_update = True

    props.init_properties_on_load()
    make_renderer.reload_blend_data()

    bpy.ops.arm.sync_proxy()

    wrd = bpy.data.worlds['Arm']
    wrd.arm_recompile = True

    if os.path.exists(arm.utils.get_fp() + '/Libraries'):
        libs = os.listdir(arm.utils.get_fp() + '/Libraries')
        for lib in libs:
            if os.path.isdir(arm.utils.get_fp() + '/Libraries/' + lib):
                fp = arm.utils.get_fp() + '/Libraries/' + lib
                if fp not in appended_py_paths and os.path.exists(fp + '/blender.py'):
                    sys.path.append(fp)
                    appended_py_paths.append(fp)
                    import blender
                    blender.register()

@persistent
def on_save_pre(context):
    props.init_properties_on_save()

def register():
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.append(on_scene_update_post)
    bpy.app.handlers.save_pre.append(on_save_pre)
    bpy.app.handlers.load_post.append(on_load_post)
    # On windows, on_load_post is not called when opening .blend file from explorer
    if arm.utils.get_os() == 'win' and arm.utils.get_fp() != '':
        on_load_post(None)

def unregister():
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.remove(on_scene_update_post)
    bpy.app.handlers.save_pre.remove(on_save_pre)
    bpy.app.handlers.load_post.remove(on_load_post)
