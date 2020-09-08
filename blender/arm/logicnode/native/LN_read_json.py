import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ReadJsonNode(ArmLogicTreeNode):
    """Read JSON node"""
    bl_idname = 'LNReadJsonNode'
    bl_label = 'Read JSON'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'File')
        self.add_input('NodeSocketBool', 'Use cache', default_value=1)
        self.add_output('ArmNodeSocketAction', 'Loaded')
        self.add_output('NodeSocketShader', 'Dynamic')

add_node(ReadJsonNode, category=MODULE_AS_CATEGORY, section='file')
