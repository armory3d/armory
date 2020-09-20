from arm.logicnode.arm_nodes import *

class ApplyTorqueImpulseNode(ArmLogicTreeNode):
    """Apply torque node"""
    bl_idname = 'LNApplyTorqueImpulseNode'
    bl_label = 'Apply Torque Impulse'
    arm_version = 1

    def init(self, context):
        super(ApplyTorqueImpulseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('NodeSocketVector', 'Torque')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyTorqueImpulseNode, category=PKG_AS_CATEGORY, section='force')
