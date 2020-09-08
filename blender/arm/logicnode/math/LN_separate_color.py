import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SeparateColorNode(ArmLogicTreeNode):
    '''Separate color node'''
    bl_idname = 'LNSeparateColorNode'
    bl_label = 'Separate RGB'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketColor', 'Color', default_value=[0.8, 0.8, 0.8, 1])

        self.add_output('NodeSocketFloat', 'R')
        self.add_output('NodeSocketFloat', 'G')
        self.add_output('NodeSocketFloat', 'B')

add_node(SeparateColorNode, category=MODULE_AS_CATEGORY, section='color')
