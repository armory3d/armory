from arm.logicnode.arm_nodes import *

class ApplyTorqueImpulseNode(ArmLogicTreeNode):
    """Applies torque impulse in the given rigid body."""
    bl_idname = 'LNApplyTorqueImpulseNode'
    bl_label = 'Apply Torque Impulse'
    arm_section = 'force'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmVectorSocket', 'Torque')
        self.add_input('ArmBoolSocket', 'On Local Axis')

        self.add_output('ArmNodeSocketAction', 'Out')
