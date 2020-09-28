from arm.logicnode.arm_nodes import *

class ApplyForceNode(ArmLogicTreeNode):
    """Applies a specified force to a given rigid body.

    @seeNode Apply Force At Location
    @seeNode Apply Impulse
    @seeNode Apply Impulse At Location

    @input Force: the force vector
    @input On Local Axis: if `true`, interpret the force vector as in
        object space
    """
    bl_idname = 'LNApplyForceNode'
    bl_label = 'Apply Force'
    arm_version = 1

    def init(self, context):
        super(ApplyForceNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('NodeSocketVector', 'Force')
        self.add_input('NodeSocketBool', 'On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyForceNode, category=PKG_AS_CATEGORY, section='force')
