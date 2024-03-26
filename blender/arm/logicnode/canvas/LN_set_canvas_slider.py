from arm.logicnode.arm_nodes import *


class CanvasSetSliderNode(ArmLogicTreeNode):
    """Sets the value of the given UI slider."""
    bl_idname = 'LNCanvasSetSliderNode'
    bl_label = 'Set Canvas Slider'
    arm_section = 'elements_specific'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmFloatSocket', 'Float')

        self.add_output('ArmNodeSocketAction', 'Out')
