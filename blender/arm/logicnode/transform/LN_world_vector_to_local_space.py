from arm.logicnode.arm_nodes import *

class WorldVectorToLocalSpaceNode(ArmLogicTreeNode):
    """Transform world coordinates into object local coordinates.

    @seeNode Vector to Object Orientation
    @seeNode Get World Orientation
    @seeNode Vector From Transform
    """
    bl_idname = 'LNWorldVectorToLocalSpaceNode'
    bl_label = 'World Vector to Local Space'
    arm_section = 'location'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'World')

        self.add_output('ArmVectorSocket', 'Local')
