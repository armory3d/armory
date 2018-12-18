import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetParticleSpeedNode(Node, ArmLogicTreeNode):
    '''Set particle speed node'''
    bl_idname = 'LNSetParticleSpeedNode'
    bl_label = 'Set Particle Speed'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketFloat', 'Speed')
        self.inputs[-1].default_value = 1.0
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetParticleSpeedNode, category='Animation')
