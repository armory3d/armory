from arm.logicnode.arm_nodes import *


class GetImageColorNode(ArmLogicTreeNode):
    """Gets Color of the pixel in X,Y position of: input Image, Render, Render2D and Render+Render2D.

    @input X: pixel position regarding width.
    @input Y: pixel position regarding height.

    @output Color: Color of the pixel in X,Y position.

    WARNING: Calling getPixels() on a renderTarget with non-standard non-POT dimensions 
    can cause a system crash. Ensure renderTarget resolution is a power of two
    (e.g., 256x256) or a common standard resolution (e.g., 1920x1080).

    """
    bl_idname = 'LNGetImageColorNode'
    bl_label = 'Get Image Color'
    arm_version = 1

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 0:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Image':
            self.add_input('ArmStringSocket', 'Image')
        self.add_input('ArmIntSocket', 'X')
        self.add_input('ArmIntSocket', 'Y')

    property0: HaxeEnumProperty(
    'property0',
    items = [('Image', 'Image', 'Image'),
             ('Render2D', 'Render2D', 'Render2D'),
             ('Render', 'Render', 'Render'),
             ('Render&Render2D', 'Render&Render2D', 'Render&Render2D')],
    name='', default='Image', update=remove_extra_inputs)

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Image')
        self.add_input('ArmIntSocket', 'X')
        self.add_input('ArmIntSocket', 'Y')
        self.add_output('ArmColorSocket', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
