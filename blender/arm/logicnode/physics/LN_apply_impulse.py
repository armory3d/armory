from arm.logicnode.arm_nodes import *

class ApplyImpulseNode(ArmLogicTreeNode):
    """Use to apply impulse in a rigid body."""
    bl_idname = 'LNApplyImpulseNode'
    bl_label = 'Apply Impulse'
    arm_version = 1

    def init(self, context):
        super(ApplyImpulseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('NodeSocketVector', 'Impulse')
        self.add_input('NodeSocketBool', 'On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyImpulseNode, category=PKG_AS_CATEGORY, section='force')
