from arm.logicnode.arm_nodes import *

class GetSystemLanguage(ArmLogicTreeNode):
    """Returns the language of the current system."""
    bl_idname = 'LNGetSystemLanguage'
    bl_label = 'Get System Language'
    arm_section = 'Native'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmStringSocket', 'Language')
