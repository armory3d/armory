from arm.logicnode.arm_nodes import *


class DrawTriangleNode(ArmLogicTreeNode):
    """Draws a triangle.

    @input Draw: Activate to draw the triangle on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Color: The color of the triangle.
    @input Filled: Whether the triangle is filled or only the outline is drawn.
    @input Strength: The line strength if the triangle is not filled.
    @input X/Y: Positions of the vertices of the triangle, in pixels from the top left corner.

    @output Out: Activated after the triangle has been drawn.

    @see [`kha.graphics2.Graphics.fillTriangle()`](http://kha.tech/api/kha/graphics2/Graphics.html#fillTriangle).
    """
    bl_idname = 'LNDrawTriangleNode'
    bl_label = 'Draw Triangle'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmBoolSocket', 'Filled', default_value=False)
        self.add_input('ArmFloatSocket', 'Strength', default_value=1.0)
        self.add_input('ArmFloatSocket', 'X1')
        self.add_input('ArmFloatSocket', 'Y1')
        self.add_input('ArmFloatSocket', 'X2')
        self.add_input('ArmFloatSocket', 'Y2')
        self.add_input('ArmFloatSocket', 'X3')
        self.add_input('ArmFloatSocket', 'Y3')

        self.add_output('ArmNodeSocketAction', 'Out')
