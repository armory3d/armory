from bpy.types import Node

from arm.logicnode.arm_nodes import *


class AlternateNode(ArmLogicTreeNode):
    """Alternate node"""
    bl_idname = 'LNAlternateNode'
    bl_label = 'Alternate'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', '0')
        self.outputs.new('ArmNodeSocketAction', '1')


add_node(AlternateNode, category=MODULE_AS_CATEGORY, section='flow')
