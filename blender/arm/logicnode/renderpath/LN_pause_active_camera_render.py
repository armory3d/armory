from arm.logicnode.arm_nodes import *

class PauseActiveCameraRenderNode(ArmLogicTreeNode):
    """Pause only the rendering of active camera. The logic behaviour remains active.

    @input In: Activate to set property.
    @input Pause: Pause the rendering when enabled.

    @output Out: Activated after property is set.
    """
    bl_idname = 'LNPauseActiveCameraRenderNode'
    bl_label = 'Pause Active Camera Render'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Pause', default_value=False)

        self.add_output('ArmNodeSocketAction', 'Out')
