import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SplitStringNode(ArmLogicTreeNode):
    '''Split string node'''
    bl_idname = 'LNSplitStringNode'
    bl_label = 'Split String'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketString', 'String')
        self.add_input('NodeSocketString', 'Split')

add_node(SplitStringNode, category=MODULE_AS_CATEGORY)
