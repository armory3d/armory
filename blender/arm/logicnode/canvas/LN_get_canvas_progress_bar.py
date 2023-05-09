from arm.logicnode.arm_nodes import *

class CanvasGetPBNode(ArmLogicTreeNode):
    """Returns the value of the given UI progress bar."""
    bl_idname = 'LNCanvasGetPBNode'
    bl_label = 'Get Canvas Progress Bar'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'At')
        self.add_output('ArmIntSocket', 'Max')
