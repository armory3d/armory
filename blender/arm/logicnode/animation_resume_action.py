import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ResumeActionNode(Node, ArmLogicTreeNode):
    '''Resume action node'''
    bl_idname = 'LNResumeActionNode'
    bl_label = 'Resume Action'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ResumeActionNode, category='Animation')
