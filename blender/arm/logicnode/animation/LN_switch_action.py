from arm.logicnode.arm_nodes import *

class SwitchActionNode(ArmLogicTreeNode):
    """Switch between the two given actions with interpolation."""
    bl_idname = 'LNSwitchActionNode'
    bl_label = 'Switch Action'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Action 1')
        self.add_input('ArmNodeSocketAction', 'Action 2')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimTree', 'Action 1')
        self.add_input('ArmNodeSocketAnimTree', 'Action 2')
        self.add_input('ArmBoolSocket', 'Restart', default_value = True)
        self.add_input('ArmFloatSocket', 'Time', default_value = 1.0)
        self.add_input('ArmIntSocket', 'Bone Group', default_value = -1)

        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('ArmNodeSocketAnimTree', 'Result')