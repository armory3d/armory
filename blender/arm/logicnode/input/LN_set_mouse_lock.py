import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMouseLockNode(ArmLogicTreeNode):
    '''Set Mouse Lock node'''
    bl_idname = 'LNSetMouseLockNode'
    bl_label = 'Set Mouse Lock'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Lock')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMouseLockNode, category=MODULE_AS_CATEGORY, section='mouse')
