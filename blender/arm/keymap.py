# Key shortcuts
import bpy
import arm.props_ui as props_ui
import arm.utils

arm_keymaps = []

def register():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type="WINDOW")
    km.keymap_items.new(props_ui.ArmoryPlayButton.bl_idname, type='F5', value='PRESS')
    km.keymap_items.new(props_ui.ArmoryRenderButton.bl_idname, type='F10', value='PRESS')
    if arm.utils.with_krom():
    	km.keymap_items.new(props_ui.ArmoryPlayInViewportButton.bl_idname, type='P', value='PRESS')
    else:
    	km.keymap_items.new(props_ui.ArmoryPlayButton.bl_idname, type='P', value='PRESS')
    arm_keymaps.append(km)

def unregister():
    wm = bpy.context.window_manager
    for km in arm_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del arm_keymaps[:]
