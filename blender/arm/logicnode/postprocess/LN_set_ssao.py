import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SSAOSetNode(Node, ArmLogicTreeNode):
    '''Set SSAO Effect'''
    bl_idname = 'LNSSAOSetNode'
    bl_label = 'Set SSAO'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'Radius')
        self.inputs[-1].default_value = 1.0
        self.inputs.new('NodeSocketFloat', 'Strength')
        self.inputs[-1].default_value = 5.0
        self.inputs.new('NodeSocketInt', 'Max Steps')
        self.inputs[-1].default_value = 8
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SSAOSetNode, category=MODULE_AS_CATEGORY)
