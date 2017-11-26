import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class UnparentNode(Node, ArmLogicTreeNode):
    '''Unparent node'''
    bl_idname = 'LNUnparentNode'
    bl_label = 'Unparent'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Keep Transform')
        self.inputs[-1].default_value = True
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(UnparentNode, category='Action')
