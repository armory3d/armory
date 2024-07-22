from arm.logicnode.arm_nodes import *


class DrawArcNode(ArmLogicTreeNode):
    """Draws an arc (part of a circle).

    @input Draw: Activate to draw the arc on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Color: The color of the arc.
    @input Filled: Whether the arc is filled or only the outline is drawn.
    @input Strength: The line strength if the arc is not filled.
    @input Segments: How many line segments should be used to draw the
        arc. 0 (default) = automatic.
    @input Center X/Y: The position of the arc's center, in pixels from the top left corner.
    @input Radius: The radius of the arc in pixels.
    @input Start Angle/End Angle: The angles in radians where the
        arc starts/ends, starting right of the arc's center.
    @input Exterior Angle: Whether the angles describe an Exterior angle.

    @output Out: Activated after the arc has been drawn.

    @see [`kha.graphics2.GraphicsExtension.drawArc()`](http://kha.tech/api/kha/graphics2/GraphicsExtension.html#drawArc).
    @see [`kha.graphics2.GraphicsExtension.fillArc()`](http://kha.tech/api/kha/graphics2/GraphicsExtension.html#fillArc).
    """
    bl_idname = 'LNDrawArcNode'
    bl_label = 'Draw Arc'
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
        self.add_input('ArmFloatSocket', 'Radius', default_value=20.0)
        self.add_input('ArmFloatSocket', 'Start Angle')
        self.add_input('ArmFloatSocket', 'End Angle')
        self.add_input('ArmBoolSocket', 'Exterior Angle', default_value=False)

        self.add_output('ArmNodeSocketAction', 'Out')
