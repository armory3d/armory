from arm.logicnode.arm_nodes import *

class CursorInRegionNode(ArmLogicTreeNode):
    """Detect cursor in specific region.

    @input Center X/Y: The position of the center in pixels.
    @input Width: Width of the region in pixels.
    @input Height: Height of the region in pixels.
    @input Angle: Rotation angle in radians. Rotation is clockwise.

    @output On Enter: Activated after the cursor enters the region.
    @output On Exit: Activated after the cursor exits the region.
    @output Is Inside: True if inside the region. False otherwise.
    """
    bl_idname = 'LNCursorInRegionNode'
    bl_label = 'Cursor In Region'
    arm_section = 'mouse'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('rectangle', 'Rectangle', 'Rectangular region'),
                 ('ellipse', 'Ellipse', 'Elliptical or Circular region')],
        name='', default='rectangle')

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Center X')
        self.add_input('ArmFloatSocket', 'Center Y')
        self.add_input('ArmFloatSocket', 'Width')
        self.add_input('ArmFloatSocket', 'Height')
        self.add_input('ArmFloatSocket', 'Angle')
        self.add_output('ArmNodeSocketAction', 'On Enter')
        self.add_output('ArmNodeSocketAction', 'On Exit')
        self.add_output('ArmBoolSocket', 'Is Inside')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
