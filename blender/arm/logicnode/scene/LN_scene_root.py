import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SceneRootNode(ArmLogicTreeNode):
    """Scene root node"""
    bl_idname = 'LNSceneRootNode'
    bl_label = 'Scene Root'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(SceneRootNode, category=MODULE_AS_CATEGORY)
