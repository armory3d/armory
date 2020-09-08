import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class StringNode(ArmLogicTreeNode):
    '''String node'''
    bl_idname = 'LNStringNode'
    bl_label = 'String'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketString', 'Value')
        self.add_output('NodeSocketString', 'String', is_var=True)

add_node(StringNode, category=MODULE_AS_CATEGORY)
