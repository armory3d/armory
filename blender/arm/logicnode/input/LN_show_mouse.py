from arm.logicnode.arm_nodes import *

class ShowMouseNode(ArmLogicTreeNode):
    """Show Mouse node"""
    bl_idname = 'LNShowMouseNode'
    bl_label = 'Show Mouse'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Show')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ShowMouseNode, category=MODULE_AS_CATEGORY, section='mouse')
