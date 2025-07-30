from arm.logicnode.arm_nodes import *


class DrawLineNode(ArmLogicTreeNode):
    """Draws a line.

    @input Draw: Activate to draw the line on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Color: The color of the line.
    @input Strength: The line strength.
    @input X1/Y1/X2/Y2: The position of line's two end points, in pixels from the top left corner.

    @output Out: Activated after the line has been drawn.

    @see [`kha.graphics2.Graphics.drawLine()`](http://kha.tech/api/kha/graphics2/Graphics.html#drawLine).
    """
    bl_idname = 'LNDrawLineNode'
    bl_label = 'Draw Line'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Strength', default_value=1.0)
        self.add_input('ArmIntSocket', 'X1')
        self.add_input('ArmIntSocket', 'Y1')
        self.add_input('ArmIntSocket', 'X2')
        self.add_input('ArmIntSocket', 'Y2')

        self.add_output('ArmNodeSocketAction', 'Out')
