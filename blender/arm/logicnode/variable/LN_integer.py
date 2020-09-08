import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IntegerNode(ArmLogicTreeNode):
    """Int node"""
    bl_idname = 'LNIntegerNode'
    bl_label = 'Integer'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketInt', 'Value')
        self.add_output('NodeSocketInt', 'Int', is_var=True)

add_node(IntegerNode, category=MODULE_AS_CATEGORY)
