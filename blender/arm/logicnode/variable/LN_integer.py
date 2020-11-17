from arm.logicnode.arm_nodes import *

class IntegerNode(ArmLogicTreeNode):
    """Stores the given integer (a whole number) as a variable."""
    bl_idname = 'LNIntegerNode'
    bl_label = 'Integer'
    arm_version = 1

    def init(self, context):
        super(IntegerNode, self).init(context)
        self.add_input('NodeSocketInt', 'Int In')
        self.add_output('NodeSocketInt', 'Int Out', is_var=1)
