from arm.logicnode.arm_nodes import *

class ApplyTorqueNode(ArmLogicTreeNode):
    """Applies torque to the given rigid body."""
    bl_idname = 'LNApplyTorqueNode'
    bl_label = 'Apply Torque'
    arm_section = 'force'
    arm_version = 1

    def init(self, context):
        super(ApplyTorqueNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('NodeSocketVector', 'Torque')
        self.add_input('NodeSocketBool', 'On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')
