from bpy.types import Node
from arm.logicnode.arm_nodes import *


class RandomColorNode(ArmLogicTreeNode):
    """Random color node"""
    bl_idname = 'LNRandomColorNode'
    bl_label = 'Random Color'

    def init(self, context):
        self.add_output('NodeSocketColor', 'Color')


add_node(RandomColorNode, category=MODULE_AS_CATEGORY)
