import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BloomGetNode(Node, ArmLogicTreeNode):
    '''Get Bloom Effect'''
    bl_idname = 'LNBloomGetNode'
    bl_label = 'Get Bloom'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Threshold')
        self.outputs.new('NodeSocketFloat', 'Strength')
        self.outputs.new('NodeSocketFloat', 'Radius')

add_node(BloomGetNode, category=MODULE_AS_CATEGORY)
