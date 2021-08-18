from arm.logicnode.arm_nodes import *

class GetMeshNode(ArmLogicTreeNode):
    """Returns the mesh of the given object."""
    bl_idname = 'LNGetMeshNode'
    bl_label = 'Get Object Mesh'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmDynamicSocket', 'Mesh')
