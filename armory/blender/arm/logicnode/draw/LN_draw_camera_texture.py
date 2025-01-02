from arm.logicnode.arm_nodes import *


class DrawCameraTextureNode(ArmLogicTreeNode):
    """Renders the scene from the view of a specified camera and draws
    its render target to the diffuse texture of the given material.

    @input Start: Evaluate the inputs and start drawing the camera render target.
    @input Stop: Stops the rendering and drawing of the camera render target.
    @input Camera: The camera from which to render.
    @input Object: Object of which to choose the material in the `Material Slot` input.
    @input Material Slot: Index of the material slot of which the diffuse
        texture is replaced with the camera's render target.

    @output On Start: Activated after the `Start` input has been activated.
    @output On Stop: Activated after the `Stop` input has been activated.
    """
    bl_idname = 'LNDrawCameraTextureNode'
    bl_label = 'Draw Camera to Texture'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmIntSocket', 'Material Slot')

        self.add_output('ArmNodeSocketAction', 'On Start')
        self.add_output('ArmNodeSocketAction', 'On Stop')
