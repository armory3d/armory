from arm.logicnode.arm_nodes import *

class ApplyImpulseNode(ArmLogicTreeNode):
    """Applies impulse in the given rigid body.

    @seeNode Apply Impulse At Location
    @seeNode Apply Force
    @seeNode Apply Force At Location

    @input Impulse: the impulse vector
    @input On Local Axis: if `true`, interpret the impulse vector as in
        object space
    """
    bl_idname = 'LNApplyImpulseNode'
    bl_label = 'Apply Impulse'
    arm_section = 'force'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmVectorSocket', 'Impulse')
        self.add_input('ArmBoolSocket', 'On Local Axis')

        self.add_output('ArmNodeSocketAction', 'Out')
