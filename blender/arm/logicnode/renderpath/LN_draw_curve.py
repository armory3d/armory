from arm.logicnode.arm_nodes import *


class DrawCurveNode(ArmLogicTreeNode):
    """Draws a cubic bezier curve with two control points.

    @input Draw: Activate to draw the curve on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Color: The color of the curve.
    @input Strength: The line strength.
    @input Segments: How many line segments should be used to draw the curve.
    @input Start Point X/Y: The position of starting point of the curve, in pixels from the top left corner.
    @input Control Point 1/2 X/Y: The position of control points of the curve, in pixels from the top left corner.
    @input End Point X/Y: The position of end point of the curve, in pixels from the top left corner.

    @output Out: Activated after the curve has been drawn.

    @see [`kha.graphics2.GraphicsExtension.drawCubicBezier()`](http://kha.tech/api/kha/graphics2/GraphicsExtension.html#drawCubicBezier).
    """
    bl_idname = 'LNDrawCurveNode'
    bl_label = 'Draw Curve'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Strength', default_value=1.0)
        self.add_input('ArmIntSocket', 'Segments', default_value=20)
        self.add_input('ArmFloatSocket', 'Start Point X')
        self.add_input('ArmFloatSocket', 'Start Point Y')
        self.add_input('ArmFloatSocket', 'Control Point 1 X')
        self.add_input('ArmFloatSocket', 'Control Point 1 Y')
        self.add_input('ArmFloatSocket', 'Control Point 2 X')
        self.add_input('ArmFloatSocket', 'Control Point 2 Y')
        self.add_input('ArmFloatSocket', 'End Point X')
        self.add_input('ArmFloatSocket', 'End Point Y')

        self.add_output('ArmNodeSocketAction', 'Out')
