import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ScaleObjectNode(ArmLogicTreeNode):
    """Scale object node"""
    bl_idname = 'LNScaleObjectNode'
    bl_label = 'Scale Object'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Vector')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ScaleObjectNode, category=MODULE_AS_CATEGORY, section='scale')
