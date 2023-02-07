from arm.logicnode.arm_nodes import *


class DrawTextAreaStringNode(ArmLogicTreeNode):
    """Draws a string.

    @input Length: length of the text area string can be determined by the amount of lines desired or the amount of characters in a line.
    @input Draw: Activate to draw the string on this frame. The input must
        be (indirectly) called from an `On Render2D` node.
    @input String: The string to draw as a text area.
    @input Font File: The filename of the font (including the extension).
        If empty and Zui is _enabled_, the default font is used. If empty
        and Zui is _disabled_, nothing is rendered.

    @length: value according to specified property above.
    @line Spacing: changes the separation between lines.
    @input Font Size: The size of the font in pixels.
    @input Color Font: The color of the string, supports alpha.
    @input Color Background: The color background of the text area, supports alpha, if no color is wanted used alpha 0.
    @input X/Y: Position of the string, in pixels from the top left corner.

    @see [`kha.graphics2.Graphics.drawString()`](http://kha.tech/api/kha/graphics2/Graphics.html#drawString).
    """
    bl_idname = 'LNDrawTextAreaStringNode'
    bl_label = 'Draw Text Area String'
    arm_section = 'draw'
    arm_version = 1

    property0: HaxeEnumProperty(
    'property0',
    items = [('Lines', 'Length of Lines', 'Length of Lines'),
             ('Chars', 'Length of Characters', 'Chars'),],
    name='', default='Lines')

    property1: HaxeEnumProperty(
    'property1',
    items = [('TextLeft', 'Hor. Align. Left', 'Hor. Align. Left'),
             ('TextCenter', 'Hor. Align. Center', 'Hor. Align. Center'),
             ('TextRight', 'Hor. Align. Right', 'Hor. Align. Right'),],
    name='', default='TextLeft')

    property2: HaxeEnumProperty(
    'property2',
    items = [('TextTop', 'Ver. Align. Top', 'Ver. Align. Top'),
             ('TextMiddle', 'Ver. Align. Middle', 'Ver. Align. Middle'),
             ('TextBottom', 'Ver. Align. Bottom', 'Ver. Align. Bottom'),],
    name='', default='TextTop')


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Draw')
        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmStringSocket', 'Font File')
        self.add_input('ArmIntSocket', 'Length', default_value=3)
        self.add_input('ArmFloatSocket', 'Line Spacing', default_value=1.0)
        self.add_input('ArmIntSocket', 'Font Size', default_value=16)
        self.add_input('ArmColorSocket', 'Color Font', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmColorSocket', 'Color Background', default_value=[0.0, 0.0, 0.0, 1.0])
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
        layout.prop(self, 'property2')
