import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetCameraNode(Node, ArmLogicTreeNode):
    """Set the active camera of the active scene."""
    bl_idname = 'LNSetCameraNode'
    bl_label = 'Set Active Camera'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')

        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetCameraNode, category='Action')
