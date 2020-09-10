import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetShadowOffscreenNode(Node, ArmLogicTreeNode):
    """Get Shadow Offscreen node"""
    bl_idname = 'LNGetShadowOffscreenNode'
    bl_label = 'Get Shadow Offscreen'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Offscreen')

add_node(GetShadowOffscreenNode, category='Value')
