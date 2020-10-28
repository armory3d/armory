from arm.logicnode.arm_nodes import *


class RandomIntegerNode(ArmLogicTreeNode):
    """Generates a random integer."""
    bl_idname = 'LNRandomIntegerNode'
    bl_label = 'Random Integer'
    arm_version = 1

    def init(self, context):
        super(RandomIntegerNode, self).init(context)
        self.add_input('NodeSocketInt', 'Min')
        self.add_input('NodeSocketInt', 'Max', default_value=2)
        self.add_output('NodeSocketInt', 'Int')
