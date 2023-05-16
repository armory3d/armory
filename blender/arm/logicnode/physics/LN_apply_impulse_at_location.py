from arm.logicnode.arm_nodes import *

class ApplyImpulseAtLocationNode(ArmLogicTreeNode):
    """Applies impulse in the given rigid body at the given position.

    @seeNode Apply Impulse
    @seeNode Apply Force
    @seeNode Apply Force At Location

    @input Impulse: the impulse vector
    @input Impulse On Local Axis: if `true`, interpret the impulse vector as in
        object space
    @input Location: the location where to apply the impulse
    @input Relative Location: if `true`, use the location relative
        to the objects location, otherwise use world coordinates
    """
    bl_idname = 'LNApplyImpulseAtLocationNode'
    bl_label = 'Apply Impulse At Location'
    arm_section = 'force'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmVectorSocket', 'Impulse')
        self.add_input('ArmBoolSocket', 'Impulse On Local Axis')
        self.add_input('ArmVectorSocket', 'Location')
        self.add_input('ArmBoolSocket', 'Relative Location')

        self.add_output('ArmNodeSocketAction', 'Out')
