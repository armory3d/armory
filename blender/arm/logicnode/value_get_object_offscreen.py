import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetObjectOffscreenNode(Node, ArmLogicTreeNode):
    """Get Object Offscreen"""
    bl_idname = 'LNGetObjectOffscreenNode'
    bl_label = 'Get Object Offscreen'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Object')
        self.outputs.new('NodeSocketBool', 'Mesh')
        self.outputs.new('NodeSocketBool', 'Shadow')

add_node(GetObjectOffscreenNode, category='Value')
