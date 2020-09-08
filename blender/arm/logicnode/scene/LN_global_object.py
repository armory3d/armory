import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GlobalObjectNode(ArmLogicTreeNode):
    '''Global object node'''
    bl_idname = 'LNGlobalObjectNode'
    bl_label = 'Global Object'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(GlobalObjectNode, category=MODULE_AS_CATEGORY)
