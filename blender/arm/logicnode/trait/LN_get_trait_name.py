from arm.logicnode.arm_nodes import *

class GetTraitNameNode(ArmLogicTreeNode):
    """Returns the name and the class type of the given trait."""
    bl_idname = 'LNGetTraitNameNode'
    bl_label = 'Get Trait Name'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Trait')

        self.add_output('ArmStringSocket', 'Name')
        self.add_output('ArmStringSocket', 'Class Type')
