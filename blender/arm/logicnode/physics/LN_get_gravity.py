import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetGravityNode(ArmLogicTreeNode):
    """Get Gravity node"""
    bl_idname = 'LNGetGravityNode'
    bl_label = 'Get Gravity'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketVector', 'Gravity')

add_node(GetGravityNode, category=MODULE_AS_CATEGORY)
