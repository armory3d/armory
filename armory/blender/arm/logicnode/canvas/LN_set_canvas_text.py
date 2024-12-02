from arm.logicnode.arm_nodes import *


class CanvasSetTextNode(ArmLogicTreeNode):
    """Sets the text of the given UI element."""
    bl_idname = 'LNCanvasSetTextNode'
    bl_label = 'Set Canvas Text'
    arm_section = 'elements_general'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmStringSocket', 'Text')

        self.add_output('ArmNodeSocketAction', 'Out')
