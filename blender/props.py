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

def initProperties():
    # For object
    bpy.types.Object.geometry_cached = bpy.props.BoolProperty(name="Geometry Cached", default=False) # TODO: move to mesh type
    bpy.types.Object.instanced_children = bpy.props.BoolProperty(name="Instanced Children", default=False)
    bpy.types.Object.custom_material = bpy.props.BoolProperty(name="Custom Material", default=False)
    bpy.types.Object.custom_material_name = bpy.props.StringProperty(name="Name", default="")
    # For geometry
    bpy.types.Mesh.static_usage = bpy.props.BoolProperty(name="Static Usage", default=True)
    # For camera
    bpy.types.Camera.frustum_culling = bpy.props.BoolProperty(name="Frustum Culling", default=False)
    bpy.types.Camera.sort_front_to_back = bpy.props.BoolProperty(name="Sort Front to Back", default=False)
    bpy.types.Camera.pipeline_path = bpy.props.StringProperty(name="Pipeline Path", default="pipeline_resource/forward_pipeline")
    bpy.types.Camera.pipeline_pass = bpy.props.StringProperty(name="Pipeline Pass", default="forward")
    # For material
    bpy.types.Material.receive_shadow = bpy.props.BoolProperty(name="Receive Shadow", default=True)
    bpy.types.Material.alpha_test = bpy.props.BoolProperty(name="Alpha Test", default=False)
    bpy.types.Material.custom_shader = bpy.props.BoolProperty(name="Custom Shader", default=False)
    bpy.types.Material.custom_shader_name = bpy.props.StringProperty(name="Name", default="")
    bpy.types.Material.export_tangents = bpy.props.BoolProperty(name="Export Tangents", default=False)

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

# Menu in data region
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
            layout.prop(obj.data, 'sort_front_to_back')
            layout.prop_search(obj.data, "pipeline_path", bpy.data, "node_groups")
            layout.prop(obj.data, 'pipeline_pass')
        elif obj.type == 'MESH':
            layout.prop(obj.data, 'static_usage')

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
    initProperties()
    bpy.app.handlers.scene_update_post.append(cb_scene_update)

def unregister():
    bpy.app.handlers.scene_update_post.remove(cb_scene_update)
    bpy.utils.unregister_module(__name__)
