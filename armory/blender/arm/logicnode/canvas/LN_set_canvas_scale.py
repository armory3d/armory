from arm.logicnode.arm_nodes import *


class CanvasSetScaleNode(ArmLogicTreeNode):
    """Sets the scale of the given UI element."""
    bl_idname = 'LNCanvasSetScaleNode'
    bl_label = 'Set Canvas Scale'
    arm_section = 'elements_general'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmIntSocket', 'Height')
        self.add_input('ArmIntSocket', 'Width')

        self.add_output('ArmNodeSocketAction', 'Out')
