import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetRotationNode(ArmLogicTreeNode):
    """Get rotation node"""
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Rotation'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Euler Angles')
        self.add_output('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketFloat', 'Angle (Radians)')
        self.add_output('NodeSocketFloat', 'Angle (Degrees)')
        self.add_output('NodeSocketVector', 'Quaternion XYZ')
        self.add_output('NodeSocketFloat', 'Quaternion W')

add_node(GetRotationNode, category=MODULE_AS_CATEGORY, section='rotation')
