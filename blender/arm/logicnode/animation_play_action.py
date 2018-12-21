import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PlayActionNode(Node, ArmLogicTreeNode):
    '''Play action node'''
    bl_idname = 'LNPlayActionNode'
    bl_label = 'Play Action'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmNodeSocketAnimAction', 'Action')
        self.inputs.new('NodeSocketFloat', 'Blend')
        self.inputs[-1].default_value = 0.2
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketAction', 'Done')

add_node(PlayActionNode, category='Animation')
