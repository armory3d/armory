from arm.logicnode.arm_nodes import *


class DrawToImageNode(ArmLogicTreeNode):
    """Writes the given draw image to the given file. If the image
    already exists, the existing content of the image is overwritten.

    @input Image File: the name of the image
    @input Color: The color that the image's pixels are multiplied with.
    @input Width: width of the image file.
    @input Height: heigth of the image file.
    @input sX: sub position of first x pixel of the sub image (0 for start).
    @input sY: sub position of first y pixel of the sub image (0 for start).
    @input sWidth: width of the sub image.
    @input sHeight: height of the sub image.

    WARNING: Calling getPixels() on a renderTarget with non-standard non-POT dimensions 
    can cause a system crash. Ensure renderTarget resolution is a power of two
    (e.g., 256x256) or a common standard resolution (e.g., 1920x1080).
    """
    bl_idname = 'LNDrawToImageNode'
    bl_label = 'Draw To Image'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Image File')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmIntSocket', 'Width')
        self.add_input('ArmIntSocket', 'Height')
        self.add_input('ArmIntSocket', 'sX')
        self.add_input('ArmIntSocket', 'sY')
        self.add_input('ArmIntSocket', 'sWidth')
        self.add_input('ArmIntSocket', 'sHeight')

        self.add_output('ArmNodeSocketAction', 'Out')
