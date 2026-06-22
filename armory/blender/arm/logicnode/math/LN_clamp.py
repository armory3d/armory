from arm.logicnode.arm_nodes import *

class ClampNode(ArmLogicTreeNode):
    """Keeps the value inside the given bound.

    @seeNode Map Range
    """
    bl_idname = 'LNClampNode'
    bl_label = 'Clamp'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Value')
        self.add_input('ArmFloatSocket', 'Min')
        self.add_input('ArmFloatSocket', 'Max')

        self.add_output('ArmFloatSocket', 'Result')
