from arm.logicnode.arm_nodes import *

class CanvasGetInputTextNode(ArmLogicTreeNode):
    """Returns the input text of the given UI element."""
    bl_idname = 'LNCanvasGetInputTextNode'
    bl_label = 'Get Canvas Input Text'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmStringSocket', 'Text')
