import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ResumeTraitNode(Node, ArmLogicTreeNode):
    '''Resume trait node'''
    bl_idname = 'LNResumeTraitNode'
    bl_label = 'Resume Trait'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Trait')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ResumeTraitNode, category='Action')
