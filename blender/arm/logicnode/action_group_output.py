import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GroupOutputNode(Node, ArmLogicTreeNode):
    '''Group output node'''
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Node Group Output'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')

add_node(GroupOutputNode, category='Action')
