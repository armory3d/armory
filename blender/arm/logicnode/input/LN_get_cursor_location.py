from arm.logicnode.arm_nodes import *

class GetCursorLocationNode(ArmLogicTreeNode):
    """Returns the mouse cursor location in screen coordinates (pixels)."""
    bl_idname = 'LNGetCursorLocationNode'
    bl_label = 'Get Cursor Location'
    arm_section = 'mouse'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmIntSocket', 'X')
        self.add_output('ArmIntSocket', 'Y')
        self.add_output('ArmIntSocket', 'Inverted X')
        self.add_output('ArmIntSocket', 'Inverted Y')
