from arm.logicnode.arm_nodes import *


class CanvasGetVisibleNode(ArmLogicTreeNode):
    """Returns whether the given UI element is visible."""
    bl_idname = 'LNCanvasGetVisibleNode'
    bl_label = 'Get Canvas Visible'
    arm_section = 'elements_general'
    arm_version = 1

    def arm_init(self, context):
        self.inputs.new('ArmStringSocket', 'Element')

        self.outputs.new('ArmBoolSocket', 'Is Visible')
