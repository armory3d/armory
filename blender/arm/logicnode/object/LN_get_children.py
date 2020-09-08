import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetChildrenNode(ArmLogicTreeNode):
    """Get children node"""
    bl_idname = 'LNGetChildrenNode'
    bl_label = 'Get Children'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketArray', 'Array')

add_node(GetChildrenNode, category=MODULE_AS_CATEGORY, section='relations')
