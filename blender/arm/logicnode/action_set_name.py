import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetNameNode(Node, ArmLogicTreeNode):
    '''Set name node'''
    bl_idname = 'LNSetNameNode'
    bl_label = 'Set Name'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Name')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetNameNode, category='Action')
