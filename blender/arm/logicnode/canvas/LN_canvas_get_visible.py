import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetVisibleNode(ArmLogicTreeNode):
    """Canvas Get Visible node"""
    bl_idname = 'LNCanvasGetVisibleNode'
    bl_label = 'Canvas Get Visible'
    arm_version = 1

    def init(self, context):
        super(CanvasGetVisibleNode, self).init(context)
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('NodeSocketBool', 'Visible')

add_node(CanvasGetVisibleNode, category=PKG_AS_CATEGORY)
