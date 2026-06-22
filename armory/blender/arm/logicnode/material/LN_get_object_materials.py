from arm.logicnode.arm_nodes import *

class GetMaterialsNode(ArmLogicTreeNode):
    """Returns the materials of the given object."""
    bl_idname = 'LNGetMaterialsNode'
    bl_label = 'Get Object Materials'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketArray', 'Materials')
        self.add_output('ArmIntSocket', 'Length')
