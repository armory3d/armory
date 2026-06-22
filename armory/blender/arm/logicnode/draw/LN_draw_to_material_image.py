from arm.logicnode.arm_nodes import *


class DrawToMaterialImageNode(ArmLogicTreeNode):
    """Sets the image render target to draw to. The render target must be created using the `Create Render Target Node` first.
    @seeNode Create Render Target Node

    @input In: Executes a 2D draw sequence connected to this node

    @input Object: Object whose material image should be drawn to.
        Use `Get Scene Root` node to draw globally (all objects that share this image, and not per-object).

    @input Material: Material whose image to be drawn to.

    @input Node: Name of the parameter.

    @input Clear Image: Clear the image before drawing to it

    @output Out: Action output to be connected to other Draw Nodes

    @output Width: Width of the image

    @output Height: Height of the image
    """
    bl_idname = 'LNDrawToMaterialImageNode'
    bl_label = 'Draw To Material Image'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Material')
        self.add_input('ArmStringSocket', 'Node')
        self.add_input('ArmBoolSocket', 'Clear Image')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'Width')
        self.add_output('ArmIntSocket', 'Height')