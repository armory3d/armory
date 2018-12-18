import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class StopSpeakerNode(Node, ArmLogicTreeNode):
    '''Stop speaker node'''
    bl_idname = 'LNStopSoundNode'
    bl_label = 'Stop Speaker'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Speaker')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(StopSpeakerNode, category='Sound')
