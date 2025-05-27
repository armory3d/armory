from arm.logicnode.arm_nodes import *


class WriteImageNode(ArmLogicTreeNode):
    """Writes the given image to the given file. If the image
    already exists, the existing content of the image is overwritten.

    Aspect ratio must match display resolution ratio.

    @input Image File: the name of the image, relative to `Krom.getFilesLocation()`
    @input Camera: the render target image of the camera to write to the image file.
    @input Width: width of the image file.
    @input Height: heigth of the image file.
    @input sX: sub position of first x pixel of the sub image (0 for start).
    @input sY: sub position of first y pixel of the sub image (0 for start).
    @input sWidth: width of the sub image.
    @input sHeight: height of the sub image.

    @seeNode Read File
    """
    bl_idname = 'LNWriteImageNode'
    bl_label = 'Write Image'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Image File')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmIntSocket', 'Width')
        self.add_input('ArmIntSocket', 'Height')
        self.add_input('ArmIntSocket', 'sX')
        self.add_input('ArmIntSocket', 'sY')
        self.add_input('ArmIntSocket', 'sWidth')
        self.add_input('ArmIntSocket', 'sHeight')

        self.add_output('ArmNodeSocketAction', 'Out')