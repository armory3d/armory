import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetCursorStateNode(ArmLogicTreeNode):
    """Get Cursor State node"""
    bl_idname = 'LNGetCursorStateNode'
    bl_label = 'Get Cursor State'
    arm_version = 1

    def init(self, context):
        super(GetCursorStateNode, self).init(context)
        self.outputs.new('NodeSocketBool', 'Is Hidden Locked')
        self.outputs.new('NodeSocketBool', 'Is Hidden')
        self.outputs.new('NodeSocketBool', 'Is Locked')

add_node(GetCursorStateNode, category=PKG_AS_CATEGORY, section='mouse')
