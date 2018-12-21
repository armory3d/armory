import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetParentNode(Node, ArmLogicTreeNode):
    '''Set parent node'''
    bl_idname = 'LNSetParentNode'
    bl_label = 'Set Parent'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmNodeSocketObject', 'Parent')
        self.inputs[-1].default_value = 'Parent'
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetParentNode, category='Action')
