from arm.logicnode.arm_nodes import *

class FloatNode(ArmLogicTreeNode):
    """Stores the given float as a variable. If the set float value has more
    than 3 decimal places, the displayed value in the node will be
    rounded, but when you click on it you can still edit the exact
    value which will be used in the game as well."""
    bl_idname = 'LNFloatNode'
    bl_label = 'Float'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Float In')
        self.add_output('ArmFloatSocket', 'Float Out', is_var=True)
