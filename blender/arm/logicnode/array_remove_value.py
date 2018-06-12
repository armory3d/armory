import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayRemoveValueNode(Node, ArmLogicTreeNode):
    '''Array remove value node'''
    bl_idname = 'LNArrayRemoveValueNode'
    bl_label = 'Array Remove Value'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketShader', 'Value')

add_node(ArrayRemoveValueNode, category='Array')
