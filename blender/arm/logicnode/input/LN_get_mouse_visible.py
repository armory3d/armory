import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMouseVisibleNode(ArmLogicTreeNode):
    """Get Mouse Visible node"""
    bl_idname = 'LNGetMouseVisibleNode'
    bl_label = 'Get Mouse Visible'
    arm_version = 1

    def init(self, context):
        super(GetMouseVisibleNode, self).init(context)
        self.outputs.new('NodeSocketBool', 'Is Visible')

add_node(GetMouseVisibleNode, category=PKG_AS_CATEGORY, section='mouse')
