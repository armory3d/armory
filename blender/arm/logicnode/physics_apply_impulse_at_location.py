import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ApplyImpulseAtLocationNode(Node, ArmLogicTreeNode):
    '''Apply impulse at location node'''
    bl_idname = 'LNApplyImpulseAtLocationNode'
    bl_label = 'Apply Impulse At Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Impulse')
        self.inputs.new('NodeSocketVector', 'Location')
        self.inputs.new('NodeSocketBool', 'On Local Axis')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ApplyImpulseAtLocationNode, category='Physics')