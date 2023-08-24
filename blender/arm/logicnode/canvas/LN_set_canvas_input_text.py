from arm.logicnode.arm_nodes import *

class CanvasSetInputTextNode(ArmLogicTreeNode):
    """Sets the input text of the given UI element."""
    bl_idname = 'LNCanvasSetInputTextNode'
    bl_label = 'Set Canvas Input Text'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmStringSocket', 'Text')
