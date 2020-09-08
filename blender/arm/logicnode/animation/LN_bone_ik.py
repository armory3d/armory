import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BoneIKNode(ArmLogicTreeNode):
    """Bone Inverse Kinematics node"""
    bl_idname = 'LNBoneIKNode'
    bl_label = 'Bone IK'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Bone')
        self.add_input('NodeSocketVector', 'Goal')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(BoneIKNode, category=MODULE_AS_CATEGORY)
