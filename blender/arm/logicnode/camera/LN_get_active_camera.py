import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ActiveCameraNode(Node, ArmLogicTreeNode):
    """Get the active camera of the active scene."""
    bl_idname = 'LNActiveCameraNode'
    bl_label = 'Get Active Camera'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(ActiveCameraNode, category=MODULE_AS_CATEGORY)
