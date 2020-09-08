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
        self.add_output('NodeSocketFloat', 'Radius')
        self.add_output('NodeSocketFloat', 'Strength')
        self.add_output('NodeSocketFloat', 'Max Steps')

add_node(SSAOGetNode, category=MODULE_AS_CATEGORY)
