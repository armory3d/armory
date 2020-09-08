import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetGravityEnabledNode(ArmLogicTreeNode):
    '''Node to enable or disable gravity on a specific object.'''
    bl_idname = 'LNSetGravityEnabledNode'
    bl_label = 'Set Gravity Enabled'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketBool', 'Enabled')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetGravityEnabledNode, category=MODULE_AS_CATEGORY)
