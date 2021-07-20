from arm.logicnode.arm_nodes import *

class NavigableLocationNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNNavigableLocationNode'
    bl_label = 'Navigable Location'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Location')
