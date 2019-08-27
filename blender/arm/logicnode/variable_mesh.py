import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MeshNode(Node, ArmLogicTreeNode):
    '''Mesh node'''
    bl_idname = 'LNMeshNode'
    bl_label = 'Mesh'
    bl_icon = 'QUESTION'
    
    property0_get: PointerProperty(name='', type=bpy.types.Mesh)

    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Mesh')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_get', bpy.data, 'meshes', icon='NONE', text='')

add_node(MeshNode, category='Variable')
