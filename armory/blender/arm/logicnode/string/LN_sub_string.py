from arm.logicnode.arm_nodes import *

class SubStringNode(ArmLogicTreeNode):
    """Returns a part of the given string."""
    bl_idname = 'LNSubStringNode'
    bl_label = 'Sub String'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'String In')
        self.add_input('ArmIntSocket', 'Start')
        self.add_input('ArmIntSocket', 'End')

        self.add_output('ArmStringSocket', 'String Out')
