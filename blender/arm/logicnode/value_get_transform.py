import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetTransformNode(Node, ArmLogicTreeNode):
    '''Get transform node'''
    bl_idname = 'LNGetTransformNode'
    bl_label = 'Get Transform'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketShader', 'Transform')

add_node(GetTransformNode, category='Value')
