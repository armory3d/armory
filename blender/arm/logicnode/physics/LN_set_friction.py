import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetFrictionNode (ArmLogicTreeNode):
    """Set Friction Node"""
    bl_idname = 'LNSetFrictionNode'
    bl_label = 'Set Friction'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketFloat', 'Friction')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetFrictionNode, category=PKG_AS_CATEGORY)
