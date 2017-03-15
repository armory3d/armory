# Embedded player in Armory Space
import bpy
from bpy.types import Header
from bpy.app.translations import contexts as i18n_contexts
import arm.utils
import arm.make as make
import arm.make_state as state
import arm.log as log

class ArmorySpaceHeader(Header):
    bl_space_type = 'VIEW_ARMORY'

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        toolsettings = context.tool_settings

        row = layout.row(align=True)
        row.template_header()
        row.operator('arm.space_stop', icon='MESH_PLANE')
        if state.is_paused:
            row.operator('arm.space_resume', icon="PLAY")
        else:
            row.operator('arm.space_pause', icon="PAUSE")

        layout.label(log.header_info_text)

class ArmorySpaceStopButton(bpy.types.Operator):
    '''Switch back to 3D view'''
    bl_idname = 'arm.space_stop'
    bl_label = 'Stop'
 
    def execute(self, context):
        area = bpy.context.area
        if area == None:
            area = state.play_area
        area.type = 'VIEW_3D'
        state.is_paused = False
        log.clear()
        return{'FINISHED'}

class ArmorySpacePauseButton(bpy.types.Operator):
    '''Pause rendering'''
    bl_idname = 'arm.space_pause'
    bl_label = 'Pause'
 
    def execute(self, context):
        state.is_paused = True
        return{'FINISHED'}

class ArmorySpaceResumeButton(bpy.types.Operator):
    '''Resume rendering'''
    bl_idname = 'arm.space_resume'
    bl_label = 'Resume'
 
    def execute(self, context):
        state.is_paused = False
        return{'FINISHED'}

def register():
    if arm.utils.with_krom():
        bpy.utils.register_class(ArmorySpaceHeader)
        bpy.utils.register_class(ArmorySpaceStopButton)
        bpy.utils.register_class(ArmorySpacePauseButton)
        bpy.utils.register_class(ArmorySpaceResumeButton)

def unregister():
    if arm.utils.with_krom():
        bpy.utils.unregister_class(ArmorySpaceHeader)
        bpy.utils.unregister_class(ArmorySpaceStopButton)
        bpy.utils.unregister_class(ArmorySpacePauseButton)
        bpy.utils.unregister_class(ArmorySpaceResumeButton)
