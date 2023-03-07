from arm.logicnode.arm_nodes import *

class CanvasSetInputTextFocusNode(ArmLogicTreeNode):
    """Sets the input text focus of the given UI element."""
    bl_idname = 'LNCanvasSetInputTextFocusNode'
    bl_label = 'Set Canvas Input Text Focus'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmBoolSocket', 'Focus')
