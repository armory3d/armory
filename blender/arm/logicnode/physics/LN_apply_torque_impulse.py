from arm.logicnode.arm_nodes import *

class ApplyTorqueImpulseNode(ArmLogicTreeNode):
    """Apply torque node"""
    bl_idname = 'LNApplyTorqueImpulseNode'
    bl_label = 'Apply Torque Impulse'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Torque')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyTorqueImpulseNode, category=MODULE_AS_CATEGORY, section='force')
