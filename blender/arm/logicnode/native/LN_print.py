from arm.logicnode.arm_nodes import *

class PrintNode(ArmLogicTreeNode):
    """Print node"""
    bl_idname = 'LNPrintNode'
    bl_label = 'Print'
    arm_version = 1

    def init(self, context):
        super(PrintNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'String')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PrintNode, category=PKG_AS_CATEGORY)
