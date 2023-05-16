from arm.logicnode.arm_nodes import *

class KeyInterpolateNode(ArmLogicTreeNode):
    """Linearly interpolate to 1.0 if input is true and interpolate to 0.0 if input is false.
    @input Key State: Interpolate to 1.0 if true and 0.0 if false.
    @input Init: Initial value in the range 0.0 to 1.0.
    @input Rate: Rate of interpolation.
    """
    bl_idname = 'LNKeyInterpolateNode'
    bl_label = 'Key Interpolate Node'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmBoolSocket', 'Key State')
        self.add_input('ArmFloatSocket', 'Init', default_value=0.0)
        self.add_input('ArmFloatSocket', 'Rate')

        self.add_output('ArmFloatSocket', 'Result')
