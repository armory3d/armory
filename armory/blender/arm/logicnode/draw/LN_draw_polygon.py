from arm.logicnode.arm_nodes import *

class DrawPolygonNode(ArmLogicTreeNode):
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
    bl_idname = 'LNDrawPolygonNode'
    bl_label = 'Draw Polygon'
    arm_section = 'draw'
    arm_version = 2
    min_inputs = 6

    num_choices: IntProperty(default=1, min=0)

    def __init__(self, *args, **kwargs):
        super(DrawPolygonNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmBoolSocket', 'Filled', default_value=False)
        self.add_input('ArmFloatSocket', 'Strength', default_value=1.0)
        self.add_input('ArmFloatSocket', 'Origin X')
        self.add_input('ArmFloatSocket', 'Origin Y')

        self.add_output('ArmNodeSocketAction', 'Out')

    def add_sockets(self):
        self.add_input('ArmFloatSocket', 'X' + str(self.num_choices))
        self.add_input('ArmFloatSocket', 'Y' + str(self.num_choices))
        self.num_choices += 1

    def remove_sockets(self):
        if self.num_choices > 1:
            self.inputs.remove(self.inputs.values()[-1])
            self.inputs.remove(self.inputs.values()[-1])
            self.num_choices -= 1

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_call_func', text='Add Point', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_sockets'

        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'remove_sockets'
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
