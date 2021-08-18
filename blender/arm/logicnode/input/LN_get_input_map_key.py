from arm.logicnode.arm_nodes import *

class GetInputMapKeyNode(ArmLogicTreeNode):
    """Get key data if it exists in the input map."""
    bl_idname = 'LNGetInputMapKeyNode'
    bl_label = 'Get Input Map Key'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Input Map')
        self.add_input('ArmStringSocket', 'Key')

        self.add_output('ArmFloatSocket', 'Scale', default_value = 1.0)
        self.add_output('ArmFloatSocket', 'Deadzone')
