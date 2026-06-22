from arm.logicnode.arm_nodes import *


class DrawImageSequenceNode(ArmLogicTreeNode):
    """Draws a sequence of image (images changing over time). The file names
    of images used in a sequence need to follow a certain pattern:
    `<prefix><frame-index>.<extension>`, `<prefix>` is an arbitrary filename
    that must be constant for the entire sequence, `<frame-index>`
    corresponds to the frame number of the image in the sequence.
    `<extension>` is the file extension (without a period ".").

    Image file names for a valid 2-frame sequence would for example
    look like this:

    ```
    myImage1.png
    myImage2.png
    ```

    @input Start: Evaluate the image filenames and start the sequence.
        If the sequence is currently running, nothing happens. If the
        sequence has finished and `Loop` is false, this input restarts
        the sequence.
    @input Stop: Stops the sequence and its drawing.
    @input Image File Prefix: See `<prefix>` above.
    @input Image File Extension: See `<extension>` above.
    @input Color: The color that the pixels of the images are multiplied with.
    @input X/Y: Position of the images, in pixels from the top left corner.
    @input Width/Height: Size of the images in pixels. The images
        grow towards the bottom right corner.
    @input Start Index: The first `<frame-index>` of the sequence (inclusive).
    @input End Index: The last `<frame-index>` of the sequence (inclusive).
    @input Frame Duration: Duration of a frame in seconds.
    @input Loop: Whether the sequence starts again from the first frame after the last frame.
    @input Wait For Load: If true, start the sequence only after all
        image files have been loaded. If false, the sequence starts immediately,
        but images that are not yet loaded are not rendered.

    @output On Start: Activated after the sequence has started. This output
        is influenced by the `Wait For Load` input.
    @output On Stop: Activated if the sequence ends or the `Stop` input
        is activated. This is not activated when the sequence restarts
        due to looping.
    """
    bl_idname = 'LNDrawImageSequenceNode'
    bl_label = 'Draw Image Sequence'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmStringSocket', 'Image File Prefix')
        self.add_input('ArmStringSocket', 'Image File Extension')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Width')
        self.add_input('ArmFloatSocket', 'Height')
        self.add_input('ArmIntSocket', 'Start Index')
        self.add_input('ArmIntSocket', 'End Index', default_value=1)
        self.add_input('ArmFloatSocket', 'Frame Duration', default_value=1.0)
        self.add_input('ArmBoolSocket', 'Loop', default_value=True)
        self.add_input('ArmBoolSocket', 'Wait For Load', default_value=True)

        self.add_output('ArmNodeSocketAction', 'On Start')
        self.add_output('ArmNodeSocketAction', 'On Stop')
