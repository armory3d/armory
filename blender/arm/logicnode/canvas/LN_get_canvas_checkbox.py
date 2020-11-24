from arm.logicnode.arm_nodes import *

class CanvasGetCheckboxNode(ArmLogicTreeNode):
    """Returns whether the given UI checkbox is checked."""
    bl_idname = 'LNCanvasGetCheckboxNode'
    bl_label = 'Get Canvas Checkbox'
    arm_version = 1

    def init(self, context):
        super(CanvasGetCheckboxNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')

        self.add_output('NodeSocketBool', 'Is Checked')
