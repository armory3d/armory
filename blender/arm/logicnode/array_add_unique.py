import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayAddUniqueNode(Node, ArmLogicTreeNode):
    '''Array add unique node'''
    bl_idname = 'LNArrayAddUniqueNode'
    bl_label = 'Array Add Unique'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Array')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ArrayAddUniqueNode, category='Array')
