from arm.logicnode.arm_nodes import *

class AddTraitNode(ArmLogicTreeNode):
    """Adds trait to the given object."""
    bl_idname = 'LNAddTraitNode'
    bl_label = 'Add Trait to Object'
    arm_version = 1

    def init(self, context):
        super(AddTraitNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Trait')

        self.add_output('ArmNodeSocketAction', 'Out')
