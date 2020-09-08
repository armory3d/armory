import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AppendTransformNode(ArmLogicTreeNode):
    """Append transform node"""
    bl_idname = 'LNAppendTransformNode'
    bl_label = 'Append Transform'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(AppendTransformNode, category=MODULE_AS_CATEGORY)
