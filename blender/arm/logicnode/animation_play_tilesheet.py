import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PlayTilesheetNode(Node, ArmLogicTreeNode):
    '''Play tilesheet node'''
    bl_idname = 'LNPlayTilesheetNode'
    bl_label = 'Play Tilesheet'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Action')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketAction', 'Done')

add_node(PlayTilesheetNode, category='Animation')
