from arm.logicnode.arm_nodes import *

class PrintNode(ArmLogicTreeNode):
    """Print the given value to the console."""
    bl_idname = 'LNPrintNode'
    bl_label = 'Print'
    arm_version = 1

    def init(self, context):
        super(PrintNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'String')
        self.add_output('ArmNodeSocketAction', 'Out')
