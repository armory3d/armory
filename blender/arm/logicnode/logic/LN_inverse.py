from bpy.types import Node

from arm.logicnode.arm_nodes import *


class InverseNode(Node, ArmLogicTreeNode):
    """Inverse node"""
    bl_idname = 'LNInverseNode'
    bl_label = 'Inverse'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')


add_node(InverseNode, category=MODULE_AS_CATEGORY, section='flow')
