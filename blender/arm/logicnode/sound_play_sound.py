import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PlaySoundNode(Node, ArmLogicTreeNode):
    '''Play sound node'''
    bl_idname = 'LNPlaySoundNode'
    bl_label = 'Play Sound'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketOperator', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Speaker')
        self.outputs.new('ArmNodeSocketOperator', 'Out')

add_node(PlaySoundNode, category='Sound')
