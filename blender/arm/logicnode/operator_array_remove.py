import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayRemoveNode(Node, ArmLogicTreeNode):
    '''Array remove node'''
    bl_idname = 'LNArrayRemoveNode'
    bl_label = 'Array Remove'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Array")
        self.inputs.new('NodeSocketInt', "Index")
        self.outputs.new('NodeSocketShader', "Out")

add_node(ArrayRemoveNode, category='Operator')
