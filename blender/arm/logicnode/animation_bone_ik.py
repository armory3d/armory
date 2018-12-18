import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BoneIKNode(Node, ArmLogicTreeNode):
    '''Bone Inverse Kinematics node'''
    bl_idname = 'LNBoneIKNode'
    bl_label = 'Bone IK'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Bone')
        self.inputs.new('NodeSocketVector', 'Goal')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(BoneIKNode, category='Animation')
