from arm.logicnode.arm_nodes import *


class RotateRenderTargetNode(ArmLogicTreeNode):
    """Rotates the render target.

    @input In: Activate to rotate render target. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Angle: Angle in radians to rotate.
    @input Center X: X coordinate to rotate around.
    @input Center Y: Y coordinate to rotate around.
    @input Revert After: Revert rotation after all the draw calls
        are activated from this node.

    @output Out: Activated after the render target is rotated.

    @see [`kha.graphics2.Graphics.rotate()`](http://kha.tech/api/kha/graphics2/Graphics.html#rotate).
    """
    bl_idname = 'LNRotateRenderTargetNode'
    bl_label = 'Rotate Render Target'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Angle')
        self.add_input('ArmFloatSocket', 'Center X')
        self.add_input('ArmFloatSocket', 'Center Y')
        self.add_input('ArmBoolSocket', 'Revert after', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Out')
