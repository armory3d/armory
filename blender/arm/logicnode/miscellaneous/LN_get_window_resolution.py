from arm.logicnode.arm_nodes import *

class WindowInfoNode(ArmLogicTreeNode):
    """Returns the current window resolution.

    @seeNode Get Display Resolution
    """
    bl_idname = 'LNWindowInfoNode'
    bl_label = 'Get Window Resolution'
    arm_section = 'screen'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmIntSocket', 'Width')
        self.add_output('ArmIntSocket', 'Height')
