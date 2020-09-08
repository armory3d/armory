import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SendGlobalEventNode(ArmLogicTreeNode):
    """Send global event node"""
    bl_idname = 'LNSendGlobalEventNode'
    bl_label = 'Send Global Event'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Event')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SendGlobalEventNode, category=MODULE_AS_CATEGORY, section='custom')
