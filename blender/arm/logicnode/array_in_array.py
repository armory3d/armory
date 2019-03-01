import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayInArrayNode(Node, ArmLogicTreeNode):
    '''In Array node'''
    bl_idname = 'LNArrayInArrayNode'
    bl_label = 'In Array'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('NodeSocketBool', 'Bool')

add_node(ArrayInArrayNode, category='Array')
