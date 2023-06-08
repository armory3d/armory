import bpy
from bpy.props import *

class ARM_PT_DopeSheetRootMotionPanel(bpy.types.Panel):
    bl_label = 'Armory Root Motion'
    bl_idname = 'ARM_PT_DopeSheetRootMotionPanel'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_context = 'data'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        ds_mode = context.space_data.mode
        if ds_mode in {'DOPESHEET', 'ACTION'}:
            return bool(context.active_action)

    def draw(self, context):
        action = context.active_action
        layout = self.layout
        layout.label(text='Action: ' + action.name)
        layout.prop(action, 'arm_root_motion_pos')
        layout.prop(action, 'arm_root_motion_rot')

class ARM_PT_NLARootMotionPanel(bpy.types.Panel):
    bl_label = 'Armory Root Motion'
    bl_idname = 'ARM_PT_NLARootMotionPanel'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_context = 'data'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return bool(context.active_nla_strip)

    def draw(self, context):
        action = context.active_nla_strip.action
        layout = self.layout
        layout.label(text='Action: ' + action.name)
        layout.prop(action, 'arm_root_motion_pos')
        layout.prop(action, 'arm_root_motion_rot')
def register():
    bpy.utils.register_class(ARM_PT_DopeSheetRootMotionPanel)
    bpy.utils.register_class(ARM_PT_NLARootMotionPanel)
def unregister():
    bpy.utils.unregister_class(ARM_PT_NLARootMotionPanel)
    bpy.utils.unregister_class(ARM_PT_DopeSheetRootMotionPanel)
