import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ToBoolNode(ArmLogicTreeNode):
    '''To Bool Node'''
    bl_idname = 'LNToBoolNode'
    bl_label = 'To Bool'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('NodeSocketBool', 'Bool')

add_node(ToBoolNode, category=MODULE_AS_CATEGORY)
