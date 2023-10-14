from arm.logicnode.arm_nodes import *


class HideActiveCanvas(ArmLogicTreeNode):
    """Set whether the active canvas is visible.

    Note that elements of invisible canvases are not rendered and computed,
    so it is not possible to interact with those elements on the screen
    """
    bl_idname = 'LNHideActiveCanvas'
    bl_label = 'Set Global Canvas Visibility'
    bl_width_default = 200
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_input('ArmBoolSocket', 'Canvas Visible', default_value=True)
