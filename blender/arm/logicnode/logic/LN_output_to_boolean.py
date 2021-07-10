from arm.logicnode.arm_nodes import *

class ToBoolNode(ArmLogicTreeNode):
    """Converts a signal to a boolean value. If the input signal is
    active, the boolean is `true`; if not, the boolean is `false`."""
    bl_idname = 'LNToBoolNode'
    bl_label = 'Output to Boolean'
    arm_version = 1

    def init(self, context):
        super(ToBoolNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmBoolSocket', 'Bool')
