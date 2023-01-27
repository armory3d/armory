from arm.logicnode.arm_nodes import *


class DrawStringNode(ArmLogicTreeNode):
    """Draws a string.

    @input Draw: Activate to draw the string on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input String: The string to draw.
    @input Font File: The filename of the font (including the extension).
        If empty and Zui is _enabled_, the default font is used. If empty
        and Zui is _disabled_, nothing is rendered.
    @input Font Size: The size of the font in pixels.
    @input Color: The color of the string.
    @input X/Y: Position of the string, in pixels from the top left corner.

    @output Out: Activated after the string has been drawn.

    @see [`kha.graphics2.Graphics.drawString()`](http://kha.tech/api/kha/graphics2/Graphics.html#drawString).
    """
    bl_idname = 'LNDrawStringNode'
    bl_label = 'Draw String'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmStringSocket', 'Font File')
        self.add_input('ArmIntSocket', 'Font Size', default_value=16)
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')

        self.add_output('ArmNodeSocketAction', 'Out')
