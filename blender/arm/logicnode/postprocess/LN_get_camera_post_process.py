from arm.logicnode.arm_nodes import *

class CameraGetNode(ArmLogicTreeNode):
    """Returns the post-processing effects of a camera."""
    bl_idname = 'LNCameraGetNode'
    bl_label = 'Get Camera Post Process'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'F-Stop')
        self.add_output('ArmFloatSocket', 'Shutter Time')
        self.add_output('ArmFloatSocket', 'ISO')
        self.add_output('ArmFloatSocket', 'Exposure Compensation')
        self.add_output('ArmFloatSocket', 'Fisheye Distortion')
        self.add_output('ArmBoolSocket', 'Auto Focus')
        self.add_output('ArmFloatSocket', 'DOF Distance')
        self.add_output('ArmFloatSocket', 'DOF Length')
        self.add_output('ArmFloatSocket', 'DOF F-Stop')
        self.add_output('ArmFloatSocket', 'Film Grain')
