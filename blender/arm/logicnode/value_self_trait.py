import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SelfTraitNode(Node, ArmLogicTreeNode):
    '''Self trait node'''
    bl_idname = 'LNSelfTraitNode'
    bl_label = 'Self Trait'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Trait')

add_node(SelfTraitNode, category='Value')
