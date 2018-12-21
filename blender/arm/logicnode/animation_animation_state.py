import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AnimationStateNode(Node, ArmLogicTreeNode):
    '''Animation state node'''
    bl_idname = 'LNAnimationStateNode'
    bl_label = 'Animation State'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Is Playing')
        self.outputs.new('NodeSocketString', 'Action')
        self.outputs.new('NodeSocketInt', 'Frame')

add_node(AnimationStateNode, category='Animation')
