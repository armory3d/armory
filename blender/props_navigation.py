import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ArmoryGenerateNavmeshButton(bpy.types.Operator):
    '''Generate navmesh from selected meshes'''
    bl_idname = 'arm.generate_navmesh'
    bl_label = 'Generate Navmesh'
 
    def execute(self, context):
        obj = context.active_object
        if obj == None or obj.type != 'MESH':
            return{'CANCELLED'}

        # TODO: build tilecache here

        # Navmesh trait
        obj.my_traitlist.add()
        obj.my_traitlist[-1].type_prop = 'Bundled Script'
        obj.my_traitlist[-1].class_name_prop = 'NavMesh'

        # For visualization
        bpy.ops.mesh.navmesh_make('EXEC_DEFAULT')
        obj = context.active_object
        obj.hide_render = True
        obj.game_export = False

        return{'FINISHED'}

class SceneNavigationPropsPanel(bpy.types.Panel):
    bl_label = "Armory Navigation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        if scene == None:
            return

        layout.operator("arm.generate_navmesh")
        

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
