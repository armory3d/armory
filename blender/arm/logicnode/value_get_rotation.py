import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetRotationNode(Node, ArmLogicTreeNode):
    '''Get rotation node'''
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Rotation'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Euler Angles')
        self.outputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('NodeSocketFloat', 'Angle (Radians)')
        self.outputs.new('NodeSocketFloat', 'Angle (Degrees)')
        self.outputs.new('NodeSocketVector', 'Quaternion XYZ')
        self.outputs.new('NodeSocketFloat', 'Quaternion W')

add_node(GetRotationNode, category='Value')
