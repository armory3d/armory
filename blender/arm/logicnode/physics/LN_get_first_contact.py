import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetFirstContactNode(ArmLogicTreeNode):
    '''Get first contact node'''
    bl_idname = 'LNGetFirstContactNode'
    bl_label = 'Get First Contact'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(GetFirstContactNode, category=MODULE_AS_CATEGORY, section='contact')
