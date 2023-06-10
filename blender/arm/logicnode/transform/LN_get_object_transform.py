from arm.logicnode.arm_nodes import *

class GetTransformNode(ArmLogicTreeNode):
    """Returns the transformation of the given object. An object's
    transform consists of vectors describing its global location,
    rotation and scale."""
    bl_idname = 'LNGetTransformNode'
    bl_label = 'Get Object Transform'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmDynamicSocket', 'Transform')
