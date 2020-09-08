import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PauseSpeakerNode(ArmLogicTreeNode):
    '''Pause speaker node'''
    bl_idname = 'LNPauseSoundNode'
    bl_label = 'Pause Speaker'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseSpeakerNode, category=MODULE_AS_CATEGORY)
