import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetCursorStateNode(ArmLogicTreeNode):
    """Returns the state of the mouse cursor.

    @seeNode Set Cursor State

    @output Is Hidden Locked: `true` if the mouse cursor is both hidden and locked.
    @output Is Hidden: `true` if the mouse cursor is hidden.
    @output Is Locked: `true` if the mouse cursor is locked."""
    bl_idname = 'LNGetCursorStateNode'
    bl_label = 'Get Cursor State'
    arm_version = 1

    def init(self, context):
        super(GetCursorStateNode, self).init(context)
        self.outputs.new('NodeSocketBool', 'Is Hidden Locked')
        self.outputs.new('NodeSocketBool', 'Is Hidden')
        self.outputs.new('NodeSocketBool', 'Is Locked')

add_node(GetCursorStateNode, category=PKG_AS_CATEGORY, section='mouse')
