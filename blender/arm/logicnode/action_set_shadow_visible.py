import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetShadowVisibleNode(Node, ArmLogicTreeNode):
    '''Set Shadow Visible node'''
    bl_idname = 'LNSetShadowVisibleNode'
    bl_label = 'Set Shadow Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Visible')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetShadowVisibleNode, category='Action')
