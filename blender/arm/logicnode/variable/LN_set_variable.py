import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetVariableNode(ArmLogicTreeNode):
    '''Set variable node'''
    bl_idname = 'LNSetVariableNode'
    bl_label = 'Set Variable'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Variable')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetVariableNode, category=MODULE_AS_CATEGORY)
