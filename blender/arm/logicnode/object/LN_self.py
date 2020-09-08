import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SelfNode(ArmLogicTreeNode):
    '''Self node'''
    bl_idname = 'LNSelfNode'
    bl_label = 'Self'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(SelfNode, category=MODULE_AS_CATEGORY)
