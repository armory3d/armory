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
    # For geometry
    bpy.types.Object.geometry_cached = bpy.props.BoolProperty(name="Geometry cached", default=False)
    bpy.types.Object.instanced_children = bpy.props.BoolProperty(name="Instanced children", default=False)
    bpy.types.Object.custom_material = bpy.props.BoolProperty(name="Custom material", default=False)
    bpy.types.Object.custom_material_name = bpy.props.StringProperty(name="Name", default="")
    # For camera
    bpy.types.Camera.frustum_culling = bpy.props.BoolProperty(name="Frustum Culling", default=False)
    bpy.types.Camera.pipeline_path = bpy.props.StringProperty(name="Pipeline Path", default="pipeline_resource/forward_pipeline")
    bpy.types.Camera.pipeline_pass = bpy.props.StringProperty(name="Pipeline Pass", default="forward")
    # For material
    bpy.types.Material.receive_shadow = bpy.props.BoolProperty(name="Receive shadow", default=True)
    bpy.types.Material.alpha_test = bpy.props.BoolProperty(name="Alpha test", default=False)
    bpy.types.Material.custom_shader = bpy.props.BoolProperty(name="Custom shader", default=False)
    bpy.types.Material.custom_shader_name = bpy.props.StringProperty(name="Name", default="")
    bpy.types.Material.export_tangents = bpy.props.BoolProperty(name="Export tangents", default=False)

# Menu in object region
class ObjectPropsPanel(bpy.types.Panel):
    bl_label = "Cycles Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object

        if obj.type == 'MESH':
            layout.prop(obj, 'instanced_children')
            layout.prop(obj, 'custom_material')
            if obj.custom_material:
                layout.prop(obj, 'custom_material_name')

# Menu in camera region
class DataPropsPanel(bpy.types.Panel):
    bl_label = "Cycles Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object

        if obj.type == 'CAMERA':
            layout.prop(obj.data, 'frustum_culling')
            layout.prop(obj.data, 'pipeline_path')
            layout.prop(obj.data, 'pipeline_pass')

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
        layout.prop(mat, 'custom_shader')
        if mat.custom_shader:
            layout.prop(mat, 'custom_shader_name')

# Registration
def register():
    bpy.utils.register_module(__name__)
    initObjectProperties()
    bpy.app.handlers.scene_update_post.append(cb_scene_update)

def unregister():
    bpy.app.handlers.scene_update_post.remove(cb_scene_update)
    bpy.utils.unregister_module(__name__)
