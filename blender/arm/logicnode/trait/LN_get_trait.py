import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetTraitNode(ArmLogicTreeNode):
    '''Get trait node'''
    bl_idname = 'LNGetTraitNode'
    bl_label = 'Get Trait'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Name')
        self.add_output('NodeSocketShader', 'Trait')

add_node(GetTraitNode, category=MODULE_AS_CATEGORY)
