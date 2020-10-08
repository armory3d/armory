import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetVisibleNode(ArmLogicTreeNode):
    """Returns whether the given UI element is visible."""
    bl_idname = 'LNCanvasGetVisibleNode'
    bl_label = 'Get Canvas Visible'
    arm_version = 1

    def init(self, context):
        super(CanvasGetVisibleNode, self).init(context)
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('NodeSocketBool', 'Is Visible')

add_node(CanvasGetVisibleNode, category=PKG_AS_CATEGORY)
