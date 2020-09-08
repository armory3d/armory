import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SSAOSetNode(ArmLogicTreeNode):
    '''Set SSAO Effect'''
    bl_idname = 'LNSSAOSetNode'
    bl_label = 'Set SSAO'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Radius', default_value=1.0)
        self.add_input('NodeSocketFloat', 'Strength', default_value=5.0)
        self.add_input('NodeSocketInt', 'Max Steps', default_value=8)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SSAOSetNode, category=MODULE_AS_CATEGORY)
