from arm.logicnode.arm_nodes import *

class ApplyTorqueNode(ArmLogicTreeNode):
    """Use to apply torque to a rigid body."""
    bl_idname = 'LNApplyTorqueNode'
    bl_label = 'Apply Torque'
    arm_version = 1

    def init(self, context):
        super(ApplyTorqueNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('NodeSocketVector', 'Torque')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyTorqueNode, category=PKG_AS_CATEGORY, section='force')
