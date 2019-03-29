import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ApplyImpulseNode(Node, ArmLogicTreeNode):
    '''Apply impulse node'''
    bl_idname = 'LNApplyImpulseNode'
    bl_label = 'Apply Impulse'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Impulse')
        self.inputs.new('NodeSocketBool', 'On Local Axis')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ApplyImpulseNode, category='Physics')
