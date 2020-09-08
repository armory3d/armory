import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class FloatNode(ArmLogicTreeNode):
    '''Float node'''
    bl_idname = 'LNFloatNode'
    bl_label = 'Float'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketFloat', 'Value')
        self.add_output('NodeSocketFloat', 'Float', is_var=True)

add_node(FloatNode, category=MODULE_AS_CATEGORY)
