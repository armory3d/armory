from arm.logicnode.arm_nodes import *

# Class GetSystemName
class GetSystemName(ArmLogicTreeNode):
    """Returns the name of the current system."""
    bl_idname = 'LNGetSystemName'
    bl_label = 'Get System Name'
    arm_section = 'Native'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmStringSocket', 'System Name')
        self.add_output('ArmBoolSocket', 'Windows')
        self.add_output('ArmBoolSocket', 'Linux')
        self.add_output('ArmBoolSocket', 'Mac')
        self.add_output('ArmBoolSocket', 'HTML5')
        self.add_output('ArmBoolSocket', 'Android')
