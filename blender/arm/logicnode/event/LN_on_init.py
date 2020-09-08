import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnInitNode(ArmLogicTreeNode):
    """On init node"""
    bl_idname = 'LNOnInitNode'
    bl_label = 'On Init'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnInitNode, category=MODULE_AS_CATEGORY)
