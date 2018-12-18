import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RemoveTraitNode(Node, ArmLogicTreeNode):
    '''Remove trait node'''
    bl_idname = 'LNRemoveTraitNode'
    bl_label = 'Remove Trait'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Trait')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(RemoveTraitNode, category='Action')
