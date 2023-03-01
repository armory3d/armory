from arm.logicnode.arm_nodes import *

class CanvasGetTextNode(ArmLogicTreeNode):
    """Sets the text of the given UI element."""
    bl_idname = 'LNCanvasGetTextNode'
    bl_label = 'Get Canvas Text'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmStringSocket', 'String')
