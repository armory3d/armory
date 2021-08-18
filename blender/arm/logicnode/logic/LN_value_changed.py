from arm.logicnode.arm_nodes import *

class ValueChangedNode(ArmLogicTreeNode):
    """Sends a signal to `Changed` output whether the connected value is changed and a signal to `Unchanged` if the connected value returns to initial. Does not works with `null` value."""
    bl_idname = 'LNValueChangedNode'
    bl_label = 'Value Changed'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Changed')
        self.add_output('ArmNodeSocketAction', 'Unchanged')
