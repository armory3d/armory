import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayLengthNode(ArmLogicTreeNode):
    '''Array length node'''
    bl_idname = 'LNArrayLengthNode'
    bl_label = 'Array Length'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.outputs.new('NodeSocketInt', 'Length')

add_node(ArrayLengthNode, category=MODULE_AS_CATEGORY)
