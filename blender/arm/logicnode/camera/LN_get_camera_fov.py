import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetCameraFovNode(ArmLogicTreeNode):
    """Get camera FOV node"""
    bl_idname = 'LNGetCameraFovNode'
    bl_label = 'Get Camera FOV'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketFloat', 'FOV')

add_node(GetCameraFovNode, category=MODULE_AS_CATEGORY)
