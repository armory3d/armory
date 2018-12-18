import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AddTraitNode(Node, ArmLogicTreeNode):
    '''Add trait node'''
    bl_idname = 'LNAddTraitNode'
    bl_label = 'Add Trait'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Trait')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(AddTraitNode, category='Action')
