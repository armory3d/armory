import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetScaleNode(Node, ArmLogicTreeNode):
    '''Set scale node'''
    bl_idname = 'LNSetScaleNode'
    bl_label = 'Set Scale'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Scale')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetScaleNode, category='Action')
