from bpy.types import Node
from arm.logicnode.arm_nodes import *


class RandomIntegerNode(ArmLogicTreeNode):
    """Random integer node"""
    bl_idname = 'LNRandomIntegerNode'
    bl_label = 'Random Integer'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketInt', 'Min')
        self.add_input('NodeSocketInt', 'Max', default_value=2)
        self.add_output('NodeSocketInt', 'Int')


add_node(RandomIntegerNode, category=MODULE_AS_CATEGORY)
