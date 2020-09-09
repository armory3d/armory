import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMouseVisibleNode(ArmLogicTreeNode):
    """Get Mouse Visible node"""
    bl_idname = 'LNGetMouseVisibleNode'
    bl_label = 'Get Mouse Visible'

    def init(self, context):
        self.outputs.new('NodeSocketBool', 'Visible')

add_node(GetMouseVisibleNode, category=PKG_AS_CATEGORY, section='mouse')
