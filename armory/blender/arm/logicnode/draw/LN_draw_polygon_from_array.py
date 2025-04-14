from arm.logicnode.arm_nodes import *

class DrawPolygonFromArrayNode(ArmLogicTreeNode):
    """Draws a polygon.

    @input Draw: Activate to draw the polygon on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Color: The color of the polygon.
    @input Filled: Whether the polygon is filled or only the outline is drawn.
    @input Strength: The line strength if the polygon is not filled.
    @input Origin X/Origin Y: The origin position of the polygon, in pixels
        from the top left corner. This position is added to all other
        points, so they are defined relative to this position.
    @input Xn/Yn: The position of polygon's points, in pixels from `Origin X`/`Origin Y`.

    @output Out: Activated after the polygon has been drawn.

    @see [`kha.graphics2.GraphicsExtension.drawPolygon()`](http://kha.tech/api/kha/graphics2/GraphicsExtension.html#drawPolygon).
    @see [`kha.graphics2.GraphicsExtension.fillPolygon()`](http://kha.tech/api/kha/graphics2/GraphicsExtension.html#fillPolygon).
    """
    bl_idname = 'LNDrawPolygonFromArrayNode'
    bl_label = 'Draw Polygon From Array'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmBoolSocket', 'Filled', default_value=False)
        self.add_input('ArmFloatSocket', 'Strength', default_value=1.0)
        self.add_input('ArmFloatSocket', 'Origin X')
        self.add_input('ArmFloatSocket', 'Origin Y')
        self.add_input('ArmNodeSocketArray', 'Array (X, Y)')        

        self.add_output('ArmNodeSocketAction', 'Out')
