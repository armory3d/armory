import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetContactsNode(Node, ArmLogicTreeNode):
    '''Get contacts node'''
    bl_idname = 'LNGetContactsNode'
    bl_label = 'Get Contacts'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketArray', 'Array')

add_node(GetContactsNode, category='Physics')
