import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RemoveObjectNode(Node, ArmLogicTreeNode):
    '''Remove object node'''
    bl_idname = 'LNRemoveObjectNode'
    bl_label = 'Remove Object'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Object")
        self.outputs.new('NodeSocketShader', "Out")

add_node(RemoveObjectNode, category='Operator')
