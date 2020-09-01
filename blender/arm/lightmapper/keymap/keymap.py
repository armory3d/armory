import bpy

#from .. operators import build
#from .. operators import clean

tlm_keymaps = []

def register():
    pass
    # winman = bpy.context.window_manager
    # keyman = winman.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type="WINDOW")
    # keyman.keymap_items.new(build.TLM_BuildLightmaps.bl_idname, type='F6', value='PRESS')
    # keyman.keymap_items.new(clean.TLM_CleanLightmaps.bl_idname, type='F7', value='PRESS')
    # tlm_keymaps.append(keyman)

def unregister():
    pass
    # winman = bpy.context.window_manager
    # for keyman in tlm_keymaps:
    #     winman.keyconfigs.addon.keymaps.remove(keyman)
    # del tlm_keymaps[:]