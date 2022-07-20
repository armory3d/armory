from arm.logicnode.arm_nodes import *


class OnRender2DNode(ArmLogicTreeNode):
    """Registers a 2D rendering callback to activate its output on each
    frame after the frame has been drawn and other non-2D render callbacks
    have been executed.
    """
    bl_idname = 'LNOnRender2DNode'
    bl_label = 'On Render2D'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
