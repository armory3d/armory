import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SSRGetNode(ArmLogicTreeNode):
    '''Get SSR Effect'''
    bl_idname = 'LNSSRGetNode'
    bl_label = 'Get SSR'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'SSR Step')
        self.outputs.new('NodeSocketFloat', 'SSR Step Min')
        self.outputs.new('NodeSocketFloat', 'SSR Search')
        self.outputs.new('NodeSocketFloat', 'SSR Falloff')
        self.outputs.new('NodeSocketFloat', 'SSR Jitter')

add_node(SSRGetNode, category=MODULE_AS_CATEGORY)
