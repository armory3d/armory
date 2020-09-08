import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BloomSetNode(ArmLogicTreeNode):
    '''Set Bloom Effect'''
    bl_idname = 'LNBloomSetNode'
    bl_label = 'Set Bloom'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'Threshold')
        self.inputs[-1].default_value = 1.00
        self.inputs.new('NodeSocketFloat', 'Strength')
        self.inputs[-1].default_value = 3.50
        self.inputs.new('NodeSocketFloat', 'Radius')
        self.inputs[-1].default_value = 3.0
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(BloomSetNode, category=MODULE_AS_CATEGORY)
