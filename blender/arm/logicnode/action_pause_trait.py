import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PauseTraitNode(Node, ArmLogicTreeNode):
    '''Pause trait node'''
    bl_idname = 'LNPauseTraitNode'
    bl_label = 'Pause Trait'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Trait')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(PauseTraitNode, category='Action')
