from arm.logicnode.arm_nodes import *

class NotNode(ArmLogicTreeNode):
    """Inverts the plugged-in boolean. If its input is `true` it outputs `false`."""
    bl_idname = 'LNNotNode'
    bl_label = 'Invert Boolean'
    arm_version = 1

    def init(self, context):
        super(NotNode, self).init(context)
        self.add_input('NodeSocketBool', 'Bool In')
        self.add_output('NodeSocketBool', 'Bool Out')
