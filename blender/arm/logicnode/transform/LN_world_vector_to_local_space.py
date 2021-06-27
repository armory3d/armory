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

    def init(self, context):
        super(WorldVectorToLocalSpaceNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'World')
        self.add_input('NodeSocketBool', 'Subtract', default_value=True)

        self.add_output('NodeSocketVector', 'Local')
