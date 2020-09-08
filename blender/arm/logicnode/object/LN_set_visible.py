import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetVisibleNode(Node, ArmLogicTreeNode):
    '''Set visible node'''
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Bool')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetVisibleNode, category=MODULE_AS_CATEGORY, section='props')
