from arm.logicnode.arm_nodes import *


class CanvasGetCheckboxNode(ArmLogicTreeNode):
    """Returns whether the given UI checkbox is checked."""
    bl_idname = 'LNCanvasGetCheckboxNode'
    bl_label = 'Get Canvas Checkbox'
    arm_section = 'elements_specific'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmBoolSocket', 'Is Checked')
