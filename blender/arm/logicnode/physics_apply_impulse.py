import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ApplyImpulseNode(Node, ArmLogicTreeNode):
    '''Apply impulse node'''
    bl_idname = 'LNApplyImpulseNode'
    bl_label = 'Apply Impulse'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Object")
        self.inputs.new('NodeSocketVector', "Impulse")
        self.outputs.new('NodeSocketShader', "Out")

add_node(ApplyImpulseNode, category='Physics')
