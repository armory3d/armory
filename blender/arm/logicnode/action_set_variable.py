import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetVariableNode(Node, ArmLogicTreeNode):
    '''Set variable node'''
    bl_idname = 'LNSetVariableNode'
    bl_label = 'Set Variable'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Variable')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetVariableNode, category='Action')
