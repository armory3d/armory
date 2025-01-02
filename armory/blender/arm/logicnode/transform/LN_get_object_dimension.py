from arm.logicnode.arm_nodes import *

class GetDimensionNode(ArmLogicTreeNode):
    """Returns the dimension of the given object."""
    bl_idname = 'LNGetDimensionNode'
    bl_label = 'Get Object Dimension'
    arm_section = 'dimension'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmVectorSocket', 'Dimension')
