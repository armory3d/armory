from arm.logicnode.arm_nodes import *


class BranchNode(ArmLogicTreeNode):
    """Branch node"""
    bl_idname = 'LNBranchNode'
    bl_label = 'Branch'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Bool')
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')


add_node(BranchNode, category=MODULE_AS_CATEGORY)
