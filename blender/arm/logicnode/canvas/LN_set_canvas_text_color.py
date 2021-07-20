from arm.logicnode.arm_nodes import *

class CanvasSetTextColorNode(ArmLogicTreeNode):
    """Sets the color of the given UI element."""
    bl_idname = 'LNCanvasSetTextColorNode'
    bl_label = 'Set Canvas Text Color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmFloatSocket', 'R')
        self.add_input('ArmFloatSocket', 'G')
        self.add_input('ArmFloatSocket', 'B')
        self.add_input('ArmFloatSocket', 'A')

        self.add_output('ArmNodeSocketAction', 'Out')
