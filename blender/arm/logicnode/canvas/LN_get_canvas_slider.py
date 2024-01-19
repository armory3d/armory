from arm.logicnode.arm_nodes import *


class CanvasGetSliderNode(ArmLogicTreeNode):
    """Returns the value of the given UI slider."""
    bl_idname = 'LNCanvasGetSliderNode'
    bl_label = 'Get Canvas Slider'
    arm_section = 'elements_specific'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmFloatSocket', 'Float')
