from arm.logicnode.arm_nodes import *


class DrawCircleNode(ArmLogicTreeNode):
    """Draws a circle.

    @input Draw: Activate to draw the circle on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Color: The color of the circle.
    @input Filled: Whether the circle is filled or only the outline is drawn.
    @input Strength: The line strength if the circle is not filled.
    @input Segments: How many line segments should be used to draw the
        circle. 0 (default) = automatic.
    @input Center X/Y: The position of the circle's center, in pixels from the top left corner.
    @input Radius: The radius of the circle in pixels.

    @output Out: Activated after the circle has been drawn.

    @see [`kha.graphics2.GraphicsExtension.drawCircle()`](http://kha.tech/api/kha/graphics2/GraphicsExtension.html#drawCircle).
    @see [`kha.graphics2.GraphicsExtension.fillCircle()`](http://kha.tech/api/kha/graphics2/GraphicsExtension.html#fillCircle).
    """
    bl_idname = 'LNDrawCircleNode'
    bl_label = 'Draw Circle'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmBoolSocket', 'Filled', default_value=False)
        self.add_input('ArmFloatSocket', 'Strength', default_value=1.0)
        self.add_input('ArmIntSocket', 'Segments')
        self.add_input('ArmFloatSocket', 'Center X')
        self.add_input('ArmFloatSocket', 'Center Y')
        self.add_input('ArmFloatSocket', 'Radius')

        self.add_output('ArmNodeSocketAction', 'Out')
