import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetGravityNode(ArmLogicTreeNode):
    '''Set Gravity node'''
    bl_idname = 'LNSetGravityNode'
    bl_label = 'Set Gravity'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketVector', 'Gravity')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetGravityNode, category=MODULE_AS_CATEGORY)
