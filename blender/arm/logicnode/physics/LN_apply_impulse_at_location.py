from arm.logicnode.arm_nodes import *

class ApplyImpulseAtLocationNode(ArmLogicTreeNode):
    """Use to apply impulse in a rigid body at a specific location."""
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
