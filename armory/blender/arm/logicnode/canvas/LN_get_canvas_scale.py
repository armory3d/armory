from arm.logicnode.arm_nodes import *


class CanvasGetScaleNode(ArmLogicTreeNode):
    """Returns the scale of the given UI element."""
    bl_idname = 'LNCanvasGetScaleNode'
    bl_label = 'Get Canvas Scale'
    arm_section = 'elements_general'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'Height')
        self.add_output('ArmIntSocket', 'Width')
