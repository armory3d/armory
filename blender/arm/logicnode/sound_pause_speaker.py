import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PauseSpeakerNode(Node, ArmLogicTreeNode):
    '''Pause speaker node'''
    bl_idname = 'LNPauseSoundNode'
    bl_label = 'Pause Speaker'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Speaker')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(PauseSpeakerNode, category='Sound')
