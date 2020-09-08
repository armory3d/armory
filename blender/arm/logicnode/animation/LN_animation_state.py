import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AnimationStateNode(ArmLogicTreeNode):
    """Animation state node"""
    bl_idname = 'LNAnimationStateNode'
    bl_label = 'Animation State'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketBool', 'Is Playing')
        self.add_output('NodeSocketString', 'Action')
        self.add_output('NodeSocketInt', 'Frame')

add_node(AnimationStateNode, category=MODULE_AS_CATEGORY)
