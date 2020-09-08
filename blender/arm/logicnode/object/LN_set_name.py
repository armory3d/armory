import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetNameNode(ArmLogicTreeNode):
    '''Set name node'''
    bl_idname = 'LNSetNameNode'
    bl_label = 'Set Name'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Name')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetNameNode, category=MODULE_AS_CATEGORY, section='props')
