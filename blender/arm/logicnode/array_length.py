import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayLengthNode(Node, ArmLogicTreeNode):
    '''Array length node'''
    bl_idname = 'LNArrayLengthNode'
    bl_label = 'Array Length'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.outputs.new('NodeSocketInt', 'Length')

add_node(ArrayLengthNode, category='Array')
