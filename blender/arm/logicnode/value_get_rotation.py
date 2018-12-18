import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetRotationNode(Node, ArmLogicTreeNode):
    '''Get rotation node'''
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Rotation'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Rotation')

add_node(GetRotationNode, category='Value')
