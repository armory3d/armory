import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LerpVectorsNode(Node, ArmLogicTreeNode):
    '''Lerp Vectors node'''
    bl_idname = 'LNLerpVectorsNode'
    bl_label = 'Lerp Vectors'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketVector', 'Vector')
        self.inputs.new('NodeSocketVector', 'Vector')
        self.inputs.new('NodeSocketFloat', 'Time')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketVector', 'Vector')

add_node(LerpVectorsNode, category='Value')
