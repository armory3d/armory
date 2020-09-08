import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetPropertyNode(ArmLogicTreeNode):
    """Set property node"""
    bl_idname = 'LNSetPropertyNode'
    bl_label = 'Set Property'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Property')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetPropertyNode, category=MODULE_AS_CATEGORY, section='props')
