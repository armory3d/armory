import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetObjectOffscreenNode(Node, ArmLogicTreeNode):
    """Get Object Offscreen node"""
    bl_idname = 'LNGetObjectCulledNode'
    bl_label = 'Get Object Offscreen'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Offscreen')

add_node(GetObjectOffscreenNode, category='Value')
