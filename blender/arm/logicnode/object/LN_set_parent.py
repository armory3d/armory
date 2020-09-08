import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetParentNode(ArmLogicTreeNode):
    '''Set parent node'''
    bl_idname = 'LNSetParentNode'
    bl_label = 'Set Parent'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Parent', default_value='Parent')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetParentNode, category=MODULE_AS_CATEGORY, section='relations')
