import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RemoveActiveSceneNode(ArmLogicTreeNode):
    """Remove active scene node"""
    bl_idname = 'LNRemoveActiveSceneNode'
    bl_label = 'Remove Active Scene'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(RemoveActiveSceneNode, category=MODULE_AS_CATEGORY)
