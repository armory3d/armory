import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetParticleSpeedNode(ArmLogicTreeNode):
    '''Set particle speed node'''
    bl_idname = 'LNSetParticleSpeedNode'
    bl_label = 'Set Particle Speed'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketFloat', 'Speed', default_value=1.0)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetParticleSpeedNode, category=MODULE_AS_CATEGORY)
