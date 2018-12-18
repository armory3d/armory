import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayShiftNode(Node, ArmLogicTreeNode):
    '''Array shift node'''
    bl_idname = 'LNArrayShiftNode'
    bl_label = 'Array Shift'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.outputs.new('NodeSocketShader', 'Value')

add_node(ArrayShiftNode, category='Array')
