from arm.logicnode.arm_nodes import *

class HasContactArrayNode(ArmLogicTreeNode):
    """Returns whether the given rigid body has contact with other given rigid bodies."""
    bl_idname = 'LNHasContactArrayNode'
    bl_label = 'Has Contact Array'
    arm_section = 'contact'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmNodeSocketArray', 'RBs')

        self.add_output('ArmBoolSocket', 'Has Contact')
