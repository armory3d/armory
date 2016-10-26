# Embedded player in Armory Space
import bpy
from bpy.types import Header
from bpy.app.translations import contexts as i18n_contexts
import armutils
import make
import make_state as state
import log

class ArmorySpaceHeader(Header):
    bl_space_type = 'VIEW_ARMORY'
    info_text = ''

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        toolsettings = context.tool_settings

        row = layout.row(align=True)
        # row.template_header()
        row.operator('arm.space_stop', icon='MESH_PLANE')
        if state.is_paused:
            row.operator('arm.space_resume', icon="PLAY")
        else:
            row.operator('arm.space_pause', icon="PAUSE")

        layout.label(ArmorySpaceHeader.info_text)

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
    if armutils.with_chromium():
        bpy.utils.register_module(__name__)

def unregister():
    if armutils.with_chromium():
        bpy.utils.unregister_module(__name__)
