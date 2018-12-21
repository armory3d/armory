import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMouseLockNode(Node, ArmLogicTreeNode):
    '''Set Mouse Lock node'''
    bl_idname = 'LNSetMouseLockNode'
    bl_label = 'Set Mouse Lock'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Lock')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMouseLockNode, category='Input')
