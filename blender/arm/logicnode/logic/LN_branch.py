from bpy.types import Node

from arm.logicnode.arm_nodes import *


class BranchNode(ArmLogicTreeNode):
    """Branch node"""
    bl_idname = 'LNBranchNode'
    bl_label = 'Branch'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Bool')
        self.outputs.new('ArmNodeSocketAction', 'True')
        self.outputs.new('ArmNodeSocketAction', 'False')


add_node(BranchNode, category=MODULE_AS_CATEGORY)
