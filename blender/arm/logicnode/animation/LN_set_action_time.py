from arm.logicnode.arm_nodes import *

class SetActionTimeNode(ArmLogicTreeNode):
    """Sets the current action time for the given object."""
    bl_idname = 'LNSetActionTimeNode'
    bl_label = 'Set Action Time'
    bl_width_default = 200
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action ID')
        self.add_input('ArmFloatSocket', 'Time')

        self.add_output('ArmNodeSocketAction', 'Out')