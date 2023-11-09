from arm.logicnode.arm_nodes import *


class DrawVideoNode(ArmLogicTreeNode):
    """Draws a Video.

    @input Draw: Activate to draw the Video on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input Video: The filename of the Video.
    @input Color: The color that the Video's pixels are multiplied with.
    @input Left/Center/Right: Horizontal anchor point of the Video.
        0 = Left, 1 = Center, 2 = Right
    @input Top/Middle/Bottom: Vertical anchor point of the Video.
        0 = Top, 1 = Middle, 2 = Bottom
    @input X/Y: Position of the anchor point in pixels.
    @input Width/Height: Size of the Video in pixels.
    @input Angle: Rotation angle in radians. Video will be rotated cloclwiswe
        at the anchor point.

    @output Out: Activated after the Video has been drawn.

    @see [`kha.graphics2.Graphics.drawVideo()`](http://kha.tech/api/kha/graphics2/Graphics.html#drawVideo).
    """
    bl_idname = 'LNDrawVideoNode'
    bl_label = 'Draw Video'
    arm_section = 'draw'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmStringSocket', 'Video File')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmIntSocket', '0/1/2 = Left/Center/Right', default_value=0)
        self.add_input('ArmIntSocket', '0/1/2 = Top/Middle/Bottom', default_value=0)
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Width')
        self.add_input('ArmFloatSocket', 'Height')
        self.add_input('ArmFloatSocket', 'Angle')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            "LNDrawVideoNode", self.arm_version,
            "LNDrawVideoNode", 2,
            in_socket_mapping={0:0, 1:1, 2:2, 3:5, 4:6, 5:7, 6:8},
            out_socket_mapping={0:0},
        )
