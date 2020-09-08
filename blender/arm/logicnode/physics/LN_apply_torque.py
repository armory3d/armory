from arm.logicnode.arm_nodes import *

class ApplyTorqueNode(ArmLogicTreeNode):
    """Apply torque node"""
    bl_idname = 'LNApplyTorqueNode'
    bl_label = 'Apply Torque'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Torque')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyTorqueNode, category=MODULE_AS_CATEGORY, section='force')
