from arm.logicnode.arm_nodes import *


class DrawImageNode(ArmLogicTreeNode):
    """Draws an image.

    @input Draw: Activate to draw the image on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Image: The filename of the image.
    @input Color: The color that the image's pixels are multiplied with.
    @input X/Y: Position of the image, in pixels from the top left corner.
    @input Width/Height: Size of the image in pixels. The image
        grows towards the bottom right corner.

    @output Out: Activated after the image has been drawn.

    @see [`kha.graphics2.Graphics.drawImage()`](http://kha.tech/api/kha/graphics2/Graphics.html#drawImage).
    """
    bl_idname = 'LNDrawImageNode'
    bl_label = 'Draw Image'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmStringSocket', 'Image File')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Width')
        self.add_input('ArmFloatSocket', 'Height')

        self.add_output('ArmNodeSocketAction', 'Out')
