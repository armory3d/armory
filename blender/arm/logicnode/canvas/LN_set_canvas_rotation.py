from arm.logicnode.arm_nodes import *

class CanvasSetRotationNode(ArmLogicTreeNode):
    """Sets the rotation of the given UI element."""
    bl_idname = 'LNCanvasSetRotationNode'
    bl_label = 'Set Canvas Rotation'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmFloatSocket', 'Rad')

        self.add_output('ArmNodeSocketAction', 'Out')
