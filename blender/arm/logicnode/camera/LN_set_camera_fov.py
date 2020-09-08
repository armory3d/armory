import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetCameraFovNode(Node, ArmLogicTreeNode):
    """Set the camera's field of view."""
    bl_idname = 'LNSetCameraFovNode'
    bl_label = 'Set Camera FOV'
    bl_icon = 'NONE'
    bl_description = 'Set the camera\'s field of view'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketFloat', 'FOV').default_value = 0.85
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetCameraFovNode, category=MODULE_AS_CATEGORY)
