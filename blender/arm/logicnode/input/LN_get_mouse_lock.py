import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMouseLockNode(ArmLogicTreeNode):
    """Get Mouse Lock node"""
    bl_idname = 'LNGetMouseLockNode'
    bl_label = 'Get Mouse Lock'

    def init(self, context):
        self.outputs.new('NodeSocketBool', 'Lock')

add_node(GetMouseLockNode, category=PKG_AS_CATEGORY, section='mouse')
