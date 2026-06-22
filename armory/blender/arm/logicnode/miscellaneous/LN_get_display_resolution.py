from arm.logicnode.arm_nodes import *

class DisplayInfoNode(ArmLogicTreeNode):
    """Returns the current display resolution.

    @seeNode Get Window Resolution
    """
    bl_idname = 'LNDisplayInfoNode'
    bl_label = 'Get Display Resolution'
    arm_section = 'screen'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmIntSocket', 'Width')
        self.add_output('ArmIntSocket', 'Height')
