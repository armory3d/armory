from arm.logicnode.arm_nodes import *

class CanvasSetVisibleNode(ArmLogicTreeNode):
    """Sets whether the given UI element is visibile."""
    bl_idname = 'LNCanvasSetVisibleNode'
    bl_label = 'Set Canvas Visible'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmBoolSocket', 'Visible')

        self.add_output('ArmNodeSocketAction', 'Out')
