import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AnimActionNode(ArmLogicTreeNode):
    '''Anim action node'''
    bl_idname = 'LNAnimActionNode'
    bl_label = 'Action'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_output('ArmNodeSocketAnimAction', 'Action', is_var=True)

add_node(AnimActionNode, category=MODULE_AS_CATEGORY)
