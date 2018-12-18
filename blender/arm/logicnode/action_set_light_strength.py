import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetLightStrengthNode(Node, ArmLogicTreeNode):
    '''Set light strength node'''
    bl_idname = 'LNSetLightStrengthNode'
    bl_label = 'Set Light Strength'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketFloat', 'Strength')
        self.inputs[-1].default_value = 100
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetLightStrengthNode, category='Action')
