from arm.logicnode.arm_nodes import *

class CanvasSetCheckBoxNode(ArmLogicTreeNode):
    """Sets the state of the given UI checkbox."""
    bl_idname = 'LNCanvasSetCheckBoxNode'
    bl_label = 'Set Canvas Checkbox'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmBoolSocket', 'Check')

        self.add_output('ArmNodeSocketAction', 'Out')
