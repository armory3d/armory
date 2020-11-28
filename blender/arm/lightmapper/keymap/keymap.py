import bpy

tlm_keymaps = []

def register():

    if not bpy.app.background:

        winman = bpy.context.window_manager
        keyman = winman.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type="WINDOW")

        keyman.keymap_items.new('tlm.build_lightmaps', type='F6', value='PRESS')
        keyman.keymap_items.new('tlm.clean_lightmaps', type='F7', value='PRESS')
        tlm_keymaps.append(keyman)

def unregister():
    winman = bpy.context.window_manager
    for keyman in tlm_keymaps:
        winman.keyconfigs.addon.keymaps.remove(keyman)
    del tlm_keymaps[:]