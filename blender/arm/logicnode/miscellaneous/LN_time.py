import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TimeNode(ArmLogicTreeNode):
    """Time node"""
    bl_idname = 'LNTimeNode'
    bl_label = 'Time'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'Time')
        self.add_output('NodeSocketFloat', 'Delta')

add_node(TimeNode, category=MODULE_AS_CATEGORY)
