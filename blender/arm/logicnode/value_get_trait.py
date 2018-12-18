import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetTraitNode(Node, ArmLogicTreeNode):
    '''Get trait node'''
    bl_idname = 'LNGetTraitNode'
    bl_label = 'Get Trait'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Name')
        self.outputs.new('NodeSocketShader', 'Trait')

add_node(GetTraitNode, category='Value')
