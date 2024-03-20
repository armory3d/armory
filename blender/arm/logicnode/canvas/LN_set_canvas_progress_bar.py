from arm.logicnode.arm_nodes import *


class CanvasSetPBNode(ArmLogicTreeNode):
    """Sets the value of the given UI progress bar."""
    bl_idname = 'LNCanvasSetPBNode'
    bl_label = 'Set Canvas Progress Bar'
    arm_section = 'elements_specific'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmIntSocket', 'At')
        self.add_input('ArmIntSocket', 'Max')

        self.add_output('ArmNodeSocketAction', 'Out')
