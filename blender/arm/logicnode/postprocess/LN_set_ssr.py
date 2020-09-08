import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SSRSetNode(ArmLogicTreeNode):
    '''Set SSR Effect'''
    bl_idname = 'LNSSRSetNode'
    bl_label = 'Set SSR'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'SSR Step')
        self.inputs[-1].default_value = 0.04
        self.inputs.new('NodeSocketFloat', 'SSR Step Min')
        self.inputs[-1].default_value = 0.05
        self.inputs.new('NodeSocketFloat', 'SSR Search')
        self.inputs[-1].default_value = 5.0
        self.inputs.new('NodeSocketFloat', 'SSR Falloff')
        self.inputs[-1].default_value = 5.0
        self.inputs.new('NodeSocketFloat', 'SSR Jitter')
        self.inputs[-1].default_value = 0.6
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SSRSetNode, category=MODULE_AS_CATEGORY)
