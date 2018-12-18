import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayRemoveNode(Node, ArmLogicTreeNode):
    '''Array remove node'''
    bl_idname = 'LNArrayRemoveNode'
    bl_label = 'Array Remove'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketInt', 'Index')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketShader', 'Value')

add_node(ArrayRemoveNode, category='Array')
