import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetLightColorNode(ArmLogicTreeNode):
    '''Set light color node'''
    bl_idname = 'LNSetLightColorNode'
    bl_label = 'Set Light Color'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketColor', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetLightColorNode, category=MODULE_AS_CATEGORY)
