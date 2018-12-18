import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayGetNode(Node, ArmLogicTreeNode):
    '''Array get node'''
    bl_idname = 'LNArrayGetNode'
    bl_label = 'Array Get'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketInt', 'Index')
        self.outputs.new('NodeSocketShader', 'Value')

add_node(ArrayGetNode, category='Array')
