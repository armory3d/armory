from arm.logicnode.arm_nodes import *

class ApplyForceNode(ArmLogicTreeNode):
    """Applies force in the given rigid body.

    @seeNode Apply Force At Location
    @seeNode Apply Impulse
    @seeNode Apply Impulse At Location

    @input Force: the force vector
    @input On Local Axis: if `true`, interpret the force vector as in
        object space
    """
    bl_idname = 'LNApplyForceNode'
    bl_label = 'Apply Force'
    arm_section = 'force'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmVectorSocket', 'Force')
        self.add_input('ArmBoolSocket', 'On Local Axis')

        self.add_output('ArmNodeSocketAction', 'Out')
