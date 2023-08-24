from arm.logicnode.arm_nodes import *

class GetScaleNode(ArmLogicTreeNode):
    """Returns the scale of the given object."""
    bl_idname = 'LNGetScaleNode'
    bl_label = 'Get Object Scale'
    arm_section = 'scale'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmVectorSocket', 'Scale')
