import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorNode(ArmLogicTreeNode):
    '''Color node'''
    bl_idname = 'LNColorNode'
    bl_label = 'Color'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketColor', 'Color', default_value=[0.8, 0.8, 0.8, 1.0])
        self.add_output('NodeSocketColor', 'Color')

add_node(ColorNode, category=MODULE_AS_CATEGORY)
