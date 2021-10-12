from arm.logicnode.arm_nodes import *

class CanvasSetProgressBarColorNode(ArmLogicTreeNode):
    """Sets the color of the given UI element."""
    bl_idname = 'LNCanvasSetProgressBarColorNode'
    bl_label = 'Set Canvas Progress Bar Color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmNodeSocketAction', 'Out')
