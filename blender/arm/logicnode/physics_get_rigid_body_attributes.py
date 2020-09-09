import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetRigidBodyAttributesNode(Node, ArmLogicTreeNode):
    '''Get Rigid Body Attributes node'''
    bl_idname = 'LNGetRigidBodyAttributesNode'
    bl_label = 'Get Rigid Body Attributes'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketInt', 'Collision Group')
        self.outputs.new('NodeSocketInt', 'Collision Mask')
        self.outputs.new('NodeSocketBool', 'Animated')
        self.outputs.new('NodeSocketBool', 'Static')
        self.outputs.new('NodeSocketFloat', 'Angular Damping')
        self.outputs.new('NodeSocketFloat', 'Linear Damping')
        self.outputs.new('NodeSocketFloat', 'Friction')
        self.outputs.new('NodeSocketFloat', 'Mass')

add_node(GetRigidBodyAttributesNode, category='Physics')
