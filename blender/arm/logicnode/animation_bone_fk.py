import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BoneFKNode(Node, ArmLogicTreeNode):
    '''Bone Forward Kinematics node'''
    bl_idname = 'LNBoneFKNode'
    bl_label = 'Bone FK'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Bone')
        self.inputs.new('NodeSocketShader', 'Transform')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(BoneFKNode, category='Animation')
