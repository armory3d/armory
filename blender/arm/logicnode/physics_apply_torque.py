import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ApplyTorqueNode(Node, ArmLogicTreeNode):
    '''Apply torque node'''
    bl_idname = 'LNApplyTorqueNode'
    bl_label = 'Apply Torque'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Torque')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ApplyTorqueNode, category='Physics')
