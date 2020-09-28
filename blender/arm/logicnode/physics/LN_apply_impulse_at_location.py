from arm.logicnode.arm_nodes import *

class ApplyImpulseAtLocationNode(ArmLogicTreeNode):
    """Applies an impulse to a rigid body at a specified position.

    @seeNode Apply Impulse
    @seeNode Apply Force
    @seeNode Apply Force At Location

    @input Impulse: the impulse vector
    @input Impulse On Local Axis: if `true`, interpret the impulse vector as in
        object space
    @input Location: the location where to apply the impulse
    @input Location On Local Axis: if `true`, use the location relative
        to the objects location, otherwise use world coordinates
    """
    bl_idname = 'LNApplyImpulseAtLocationNode'
    bl_label = 'Apply Impulse At Location'
    arm_version = 1

    def init(self, context):
        super(ApplyImpulseAtLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('NodeSocketVector', 'Impulse')
        self.add_input('NodeSocketBool', 'Impulse On Local Axis')
        self.add_input('NodeSocketVector', 'Location')
        self.add_input('NodeSocketBool', 'Location On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyImpulseAtLocationNode, category=PKG_AS_CATEGORY, section='force')
