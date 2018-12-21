import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetRotationNode(Node, ArmLogicTreeNode):
    '''Set rotation node'''
    bl_idname = 'LNSetRotationNode'
    bl_label = 'Set Rotation'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Rotation')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetRotationNode, category='Action')
