import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *


class SeparateQuaternionNode(ArmLogicTreeNode):

    bl_idname = 'LNSeparateQuaternionNode'
    bl_label = "Separate Quaternion"
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Quaternion')
        self.outputs.new('NodeSocketFloat', 'X')
        self.outputs.new('NodeSocketFloat', 'Y')
        self.outputs.new('NodeSocketFloat', 'Z')
        self.outputs.new('NodeSocketFloat', 'W')


add_node(SeparateQuaternionNode, category=MODULE_AS_CATEGORY, section='quaternions')
