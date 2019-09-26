import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetEularRotationNode(Node, ArmLogicTreeNode):
    '''Set eular rotation node'''
    bl_idname = 'LNSetEularRotationNode'
    bl_label = 'Set Eular Rotation'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Rotation')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetEularRotationNode, category='Action')
