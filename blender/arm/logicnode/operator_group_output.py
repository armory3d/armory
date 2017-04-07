import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GroupOutputNode(Node, ArmLogicTreeNode):
    '''Group output node'''
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Group Output'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketOperator', 'In')

add_node(GroupOutputNode, category='Operator')
