from arm.logicnode.arm_nodes import *

class WhileNode(ArmLogicTreeNode):
    """While node"""
    bl_idname = 'LNWhileNode'
    bl_label = 'While'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Condition')
        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('ArmNodeSocketAction', 'Done')

add_node(WhileNode, category=PKG_AS_CATEGORY, section='flow')
