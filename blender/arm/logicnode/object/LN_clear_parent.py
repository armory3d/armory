import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ClearParentNode(ArmLogicTreeNode):
    '''Clear parent node'''
    bl_idname = 'LNClearParentNode'
    bl_label = 'Clear Parent'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketBool', 'Keep Transform', default_value=True)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ClearParentNode, category=MODULE_AS_CATEGORY, section='relations')

