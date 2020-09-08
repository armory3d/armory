import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LoopBreakNode(ArmLogicTreeNode):
    '''Loop break node'''
    bl_idname = 'LNLoopBreakNode'
    bl_label = 'Loop Break'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

add_node(LoopBreakNode, category=MODULE_AS_CATEGORY, section='flow')
