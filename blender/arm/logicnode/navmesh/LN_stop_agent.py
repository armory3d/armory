import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class StopAgentNode(ArmLogicTreeNode):
    """Stop agent node"""
    bl_idname = 'LNStopAgentNode'
    bl_label = 'Stop Agent'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(StopAgentNode, category=MODULE_AS_CATEGORY)
