import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SSAOGetNode(ArmLogicTreeNode):
    '''Get SSAO Effect'''
    bl_idname = 'LNSSAOGetNode'
    bl_label = 'Get SSAO'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Radius')
        self.outputs.new('NodeSocketFloat', 'Strength')
        self.outputs.new('NodeSocketFloat', 'Max Steps')

add_node(SSAOGetNode, category=MODULE_AS_CATEGORY)
