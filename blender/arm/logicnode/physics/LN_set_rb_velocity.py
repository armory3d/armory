from arm.logicnode.arm_nodes import *

class SetVelocityNode(ArmLogicTreeNode):
    """Sets the velocity of the given rigid body."""
    bl_idname = 'LNSetVelocityNode'
    bl_label = 'Set RB Velocity'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmVectorSocket', 'Linear')
        self.add_input('ArmVectorSocket', 'Linear Factor', default_value=[1.0, 1.0, 1.0])
        self.add_input('ArmVectorSocket', 'Angular')
        self.add_input('ArmVectorSocket', 'Angular Factor', default_value=[1.0, 1.0, 1.0])

        self.add_output('ArmNodeSocketAction', 'Out')
