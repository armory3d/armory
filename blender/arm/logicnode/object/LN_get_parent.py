import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetParentNode(ArmLogicTreeNode):
    """Get parent node"""
    bl_idname = 'LNGetParentNode'
    bl_label = 'Get Parent'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(GetParentNode, category=MODULE_AS_CATEGORY, section='relations')
