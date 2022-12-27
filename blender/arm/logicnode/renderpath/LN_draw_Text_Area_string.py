from arm.logicnode.arm_nodes import *


class DrawTextAreaStringNode(ArmLogicTreeNode):
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
        self.add_input('ArmFloatSocket', 'Lines Spacing', default_value=1.0)
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


