import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ApplyTorqueImpulseNode(Node, ArmLogicTreeNode):
    '''Apply torque node'''
    bl_idname = 'LNApplyTorqueImpulseNode'
    bl_label = 'Apply Torque Impulse'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Torque')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ApplyTorqueImpulseNode, category='Physics')
