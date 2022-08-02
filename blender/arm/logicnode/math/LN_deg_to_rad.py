from arm.logicnode.arm_nodes import *

class DegToRadNode(ArmLogicTreeNode):
    """Converts degrees to radians."""
    bl_idname = 'LNDegToRadNode'
    bl_label = 'Deg to Rad'
    arm_version = 1
    arm_section = 'angle'

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Degrees')

        self.add_output('ArmFloatSocket', 'Radians')
