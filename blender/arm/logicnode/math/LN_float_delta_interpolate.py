from arm.logicnode.arm_nodes import *

class FloatDeltaInterpolateNode(ArmLogicTreeNode):
    """Linearly interpolate to a new value with specified interpolation `Rate`.
    @input From: Value to interpolate from.
    @input To: Value to interpolate to.
    @input Delta Time: Delta Time.
    @input Rate: Rate of interpolation.
    """
    bl_idname = 'LNFloatDeltaInterpolateNode'
    bl_label = 'Float Delta Interpolate'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'From', default_value=0.0)
        self.add_input('ArmFloatSocket', 'To', default_value=1.0)
        self.add_input('ArmFloatSocket', 'Delta Time')
        self.add_input('ArmFloatSocket', 'Rate')

        self.add_output('ArmFloatSocket', 'Result')
