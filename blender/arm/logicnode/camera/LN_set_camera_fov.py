import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetCameraFovNode(ArmLogicTreeNode):
    """Set the camera's field of view."""
    bl_idname = 'LNSetCameraFovNode'
    bl_label = 'Set Camera FOV'
    bl_icon = 'NONE'
    bl_description = 'Set the camera\'s field of view'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketFloat', 'FOV', default_value=0.85)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetCameraFovNode, category=MODULE_AS_CATEGORY)
