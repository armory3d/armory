from arm.logicnode.arm_nodes import *


class CanvasGetPositionNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNCanvasGetPositionNode'
    bl_label = 'Get Canvas Position'
    arm_section = 'elements_general'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmIntSocket', 'Position')
