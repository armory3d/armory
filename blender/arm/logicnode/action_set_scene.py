import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetSceneNode(Node, ArmLogicTreeNode):
    '''Set scene node'''
    bl_idname = 'LNSetSceneNode'
    bl_label = 'Set Scene'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Scene')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketObject', 'Root')

add_node(SetSceneNode, category='Action')
