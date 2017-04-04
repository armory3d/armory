import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetVisibleNode(Node, ArmLogicTreeNode):
    '''Set visible node'''
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Visible'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Object")
        self.inputs.new('NodeSocketBool', "Bool")
        self.outputs.new('NodeSocketShader', "Out")

add_node(SetVisibleNode, category='Operator')
