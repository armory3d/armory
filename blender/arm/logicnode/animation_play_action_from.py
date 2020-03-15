import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PlayActionFromNode(Node, ArmLogicTreeNode):
    '''Play action from node'''
    bl_idname = 'LNPlayActionFromNode'
    bl_label = 'Play Action From'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmNodeSocketAnimAction', 'Action')
        self.inputs.new('NodeSocketInt', 'Start Frame')
        self.inputs.new('NodeSocketFloat', 'Blend')
        self.inputs[-1].default_value = 0.2
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketAction', 'Done')

add_node(PlayActionFromNode, category='Animation')
