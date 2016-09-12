# Embedded player in Armory Space
import bpy
from bpy.types import Header
from bpy.app.translations import contexts as i18n_contexts
import utils

class SPACEARMORY_HT_header(Header):
    bl_space_type = 'VIEW_GAME'

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        toolsettings = context.tool_settings

        row = layout.row(align=True)
        # row.template_header()
        row.operator('arm.space_stop', icon='MESH_PLANE')

class ArmorySpaceStopButton(bpy.types.Operator):
    bl_idname = 'arm.space_stop'
    bl_label = 'Stop'
 
    def execute(self, context):
        area = bpy.context.area
        area.type = 'VIEW_3D'
        return{'FINISHED'}

def register():
    if utils.with_chromium():
        bpy.utils.register_module(__name__)

def unregister():
    if utils.with_chromium():
        bpy.utils.unregister_module(__name__)
