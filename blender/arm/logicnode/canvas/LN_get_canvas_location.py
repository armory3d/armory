from arm.logicnode.arm_nodes import *

class CanvasGetLocationNode(ArmLogicTreeNode):
    """Returns the location of the given UI element (pixels)."""
    bl_idname = 'LNCanvasGetLocationNode'
    bl_label = 'Get Canvas Location'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'X')
        self.add_output('ArmIntSocket', 'Y')
