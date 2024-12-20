from arm.logicnode.arm_nodes import *


class DrawRoundedRectNode(ArmLogicTreeNode):
    """Draws a rectangle.

    @input Draw: Activate to draw the rectangle on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Color: The color of the rectangle.
    @input Filled: Whether the rectangle is filled or only the outline is drawn.
    @input Strength: The line strength if the rectangle is not filled.
    @input Left/Center/Right: Horizontal anchor point of the rectangel.
        0 = Left, 1 = Center, 2 = Right
    @input Top/Middle/Bottom: Vertical anchor point of the rectangel.
        0 = Top, 1 = Middle, 2 = Bottom
    @input Segments: number of points to consider for rounded rect corners.
    @input Radius: radius of the rounded rect.
    @input X/Y: Position of the anchor point in pixels.
    @input Width/Height: Size of the rectangle in pixels.
    @input Angle: Rotation angle in radians. Rectangle will be rotated cloclwiswe
        at the anchor point.

    @output Out: Activated after the rectangle has been drawn.

    @see [`kha.graphics2.Graphics.drawRect()`](http://kha.tech/api/kha/graphics2/Graphics.html#drawRect).
    @see [`kha.graphics2.Graphics.fillRect()`](http://kha.tech/api/kha/graphics2/Graphics.html#fillRect).
    """
    bl_idname = 'LNDrawRoundedRectNode'
    bl_label = 'Draw Rounded Rect'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmBoolSocket', 'Filled', default_value=False)
        self.add_input('ArmFloatSocket', 'Strength', default_value=1.0)
        self.add_input('ArmIntSocket', '0/1/2 = Left/Center/Right', default_value=0)
        self.add_input('ArmIntSocket', '0/1/2 = Top/Middle/Bottom', default_value=0)
        self.add_input('ArmIntSocket', 'Segments', default_value=10)
        self.add_input('ArmFloatSocket', 'Radius')
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Width')
        self.add_input('ArmFloatSocket', 'Height')
        self.add_input('ArmFloatSocket', 'Angle')

        self.add_output('ArmNodeSocketAction', 'Out')
