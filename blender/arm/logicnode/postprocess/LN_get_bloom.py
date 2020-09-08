import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BloomGetNode(ArmLogicTreeNode):
    """Get Bloom Effect"""
    bl_idname = 'LNBloomGetNode'
    bl_label = 'Get Bloom'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'Threshold')
        self.add_output('NodeSocketFloat', 'Strength')
        self.add_output('NodeSocketFloat', 'Radius')

add_node(BloomGetNode, category=MODULE_AS_CATEGORY)
