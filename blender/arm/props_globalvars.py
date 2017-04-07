import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ArmGlobalVarsPropsPanel(bpy.types.Panel):
    bl_label = "Armory Global Variables"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
 
    def draw(self, context):
        layout = self.layout

def register():
    bpy.utils.register_class(ArmGlobalVarsPropsPanel)

def unregister():
    bpy.utils.unregister_class(ArmGlobalVarsPropsPanel)
