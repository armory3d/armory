from arm.logicnode.arm_nodes import *

class FloatNode(ArmLogicTreeNode):
    """Stores the given float as a variable. If the set float value has more
    than 3 decimal places, the displayed value in the node will be
    rounded, but when you click on it you can still edit the exact
    value which will be used in the game as well."""
    bl_idname = 'LNFloatNode'
    bl_label = 'Float'
    arm_version = 1

    def init(self, context):
        super(FloatNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Float In')
        self.add_output('NodeSocketFloat', 'Float Out', is_var=1)
