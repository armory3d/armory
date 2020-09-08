import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetLocationNode(ArmLogicTreeNode):
    """Set location node"""
    bl_idname = 'LNSetLocationNode'
    bl_label = 'Set Location'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Location')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetLocationNode, category=MODULE_AS_CATEGORY, section='location')
