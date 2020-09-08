import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayInArrayNode(ArmLogicTreeNode):
    """In Array node"""
    bl_idname = 'LNArrayInArrayNode'
    bl_label = 'In Array'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('NodeSocketBool', 'Bool')

add_node(ArrayInArrayNode, category=MODULE_AS_CATEGORY)
