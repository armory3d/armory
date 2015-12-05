import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *

def cb_scene_update(context):
    edit_obj = bpy.context.edit_object
    if edit_obj is not None and edit_obj.is_updated_data is True:
        edit_obj.geometry_cached = False

def initObjectProperties():
    bpy.types.Object.geometry_cached = bpy.props.BoolProperty(name="Geometry cached", default=False)
    bpy.types.Object.instanced_children = bpy.props.BoolProperty(name="Instanced children", default=False)
    bpy.types.Material.receive_shadow = bpy.props.BoolProperty(name="Receive shadow", default=True)
    bpy.types.Material.alpha_test = bpy.props.BoolProperty(name="Alpha test", default=False)
    bpy.types.Material.export_tangents = bpy.props.BoolProperty(name="Export tangents", default=False)
    bpy.app.handlers.scene_update_post.append(cb_scene_update)
    #bpy.app.handlers.scene_update_post.remove(cb_scene_update)

initObjectProperties()


# Menu in object region
class ToolsPropsPanel(bpy.types.Panel):
    bl_label = "Cycles Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object

        if obj.type == 'MESH':
            layout.prop(obj, 'instanced_children')

# Menu in materials region
class MatsPropsPanel(bpy.types.Panel):
    bl_label = "Cycles Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
 
    def draw(self, context):
        layout = self.layout
        mat = bpy.context.material

        layout.prop(mat, 'receive_shadow')
        layout.prop(mat, 'alpha_test')

# Registration
bpy.utils.register_module(__name__)
