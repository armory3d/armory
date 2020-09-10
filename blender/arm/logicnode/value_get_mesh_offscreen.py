import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMeshOffscreenNode(Node, ArmLogicTreeNode):
    '''Get Mesh Offscreen node'''
    bl_idname = 'LNGetMeshOffscreenNode'
    bl_label = 'Get Mesh Offscreen'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Offscreen')

add_node(GetMeshOffscreenNode, category='Value')
