import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetNameNode(ArmLogicTreeNode):
    """Get name node"""
    bl_idname = 'LNGetNameNode'
    bl_label = 'Get Name'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketString', 'Name')

add_node(GetNameNode, category=MODULE_AS_CATEGORY, section='props')
