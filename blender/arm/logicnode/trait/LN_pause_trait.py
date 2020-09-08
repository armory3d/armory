import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PauseTraitNode(ArmLogicTreeNode):
    '''Pause trait node'''
    bl_idname = 'LNPauseTraitNode'
    bl_label = 'Pause Trait'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseTraitNode, category=MODULE_AS_CATEGORY)
