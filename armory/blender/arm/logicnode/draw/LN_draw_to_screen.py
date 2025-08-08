from arm.logicnode.arm_nodes import *


class DrawToScreenNode(ArmLogicTreeNode):
    """Draws a Render Target image to screen.

    @input In: Activate to draw the Render Target image to screen.
    @input Draw Width/Height: Size of the Render Target image in pixels.
    @input Image: The filename of the image.
    @input Color: The color that the image's pixels are multiplied with.
    @input Left/Center/Right: Horizontal anchor point of the image.
        0 = Left, 1 = Center, 2 = Right
    @input Top/Middle/Bottom: Vertical anchor point of the image.
        0 = Top, 1 = Middle, 2 = Bottom
    @input X/Y: Position of the anchor point in pixels.
    @input Width/Height: Size of the sub image in pixels.
    @input sX/Y: Position of the sub anchor point in pixels.
    @input sWidth/Height: Size of the image in pixels.
    @input Angle: Rotation angle in radians. Image will be rotated cloclwiswe
        at the anchor point.
    @input Clear Image: Clear the image before drawing to it

    @output Out: Activated after the image has been drawn.

    @see [`kha.graphics2.Graphics.drawImage()`](http://kha.tech/api/kha/graphics2/Graphics.html#drawImage).
    """
    bl_idname = 'LNDrawToScreenNode'
    bl_label = 'Draw To Screen'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmIntSocket', 'Draw Width')
        self.add_input('ArmIntSocket', 'Draw Height')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmIntSocket', '0/1/2 = Left/Center/Right', default_value=0)
        self.add_input('ArmIntSocket', '0/1/2 = Top/Middle/Bottom', default_value=0)
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Width')
        self.add_input('ArmFloatSocket', 'Height')
        self.add_input('ArmFloatSocket', 'sX')
        self.add_input('ArmFloatSocket', 'sY')
        self.add_input('ArmFloatSocket', 'sWidth')
        self.add_input('ArmFloatSocket', 'sHeight')
        self.add_input('ArmFloatSocket', 'Angle')
        self.add_input('ArmBoolSocket', 'Clear Image')

        self.add_output('ArmNodeSocketAction', 'Out')