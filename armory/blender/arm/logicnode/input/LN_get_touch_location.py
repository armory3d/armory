from arm.logicnode.arm_nodes import *

class GetTouchLocationNode(ArmLogicTreeNode):
    """Returns the location of the last touch event in screen coordinates (pixels)."""
    bl_idname = 'LNGetTouchLocationNode'
    bl_label = 'Get Touch Location'
    arm_section = 'surface'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmIntSocket', 'X')
        self.add_output('ArmIntSocket', 'Y')
        self.add_output('ArmIntSocket', 'Inverted X')
        self.add_output('ArmIntSocket', 'Inverted Y')
