from arm.logicnode.arm_nodes import *

class CreateRenderTargetNode(ArmLogicTreeNode):
    """Create a render target and set it as parameter to the specified object material.
        This image can be then drawn to using `Draw To Material Image Node`. In most cases, the render target needs to be created just once.

    @seeNode Get Scene Root

    @seeNode Draw To Material Image Node

    @input Object: Object whose material parameter should change. Use `Get Scene Root` node to set parameter globally.

    @input Per Object:
        - `Enabled`: Set material parameter specific to this object. Global parameter will be ignored.
        - `Disabled`: Set parameter globally, including this object.

    @input Material: Material whose parameter to be set.

    @input Node: Name of the parameter.

    @input Width: Width of the render target image created.

    @input Height: Height of the render target image created.
    """

    bl_idname = 'LNCreateRenderTargetNode'
    bl_label = 'Create Render Target'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Per Object')
        self.add_input('ArmDynamicSocket', 'Material')
        self.add_input('ArmStringSocket', 'Node')
        self.add_input('ArmIntSocket', 'Width')
        self.add_input('ArmIntSocket', 'Height')

        self.add_output('ArmNodeSocketAction', 'Out')