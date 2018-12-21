import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArraySetNode(Node, ArmLogicTreeNode):
    '''Array set node'''
    bl_idname = 'LNArraySetNode'
    bl_label = 'Array Set'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketInt', 'Index')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ArraySetNode, category='Array')
