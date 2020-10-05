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
    arm_version = 1

    def init(self, context):
        super(ApplyImpulseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('NodeSocketVector', 'Impulse')
        self.add_input('NodeSocketBool', 'On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyImpulseNode, category=PKG_AS_CATEGORY, section='force')
