import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMouseLockNode(ArmLogicTreeNode):
    """Get Mouse Lock node"""
    bl_idname = 'LNGetMouseLockNode'
    bl_label = 'Get Mouse Lock'
    arm_version = 1

    def init(self, context):
        super(GetMouseLockNode, self).init(context)
        self.outputs.new('NodeSocketBool', 'Is Locked')

add_node(GetMouseLockNode, category=PKG_AS_CATEGORY, section='mouse')
