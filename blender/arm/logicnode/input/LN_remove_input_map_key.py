from arm.logicnode.arm_nodes import *

class RemoveInputMapKeyNode(ArmLogicTreeNode):
    """Remove input map key."""
    bl_idname = 'LNRemoveInputMapKeyNode'
    bl_label = 'Remove Input Map Key'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Input Map')
        self.add_input('ArmStringSocket', 'Key')

        self.add_output('ArmNodeSocketAction', 'Out')
