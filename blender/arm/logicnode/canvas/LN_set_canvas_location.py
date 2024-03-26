from arm.logicnode.arm_nodes import *


class CanvasSetLocationNode(ArmLogicTreeNode):
    """Sets the location of the given UI element."""
    bl_idname = 'LNCanvasSetLocationNode'
    bl_label = 'Set Canvas Location'
    arm_section = 'elements_general'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')

        self.add_output('ArmNodeSocketAction', 'Out')
