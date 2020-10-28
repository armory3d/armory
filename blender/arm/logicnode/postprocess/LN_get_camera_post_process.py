from arm.logicnode.arm_nodes import *

class CameraGetNode(ArmLogicTreeNode):
    """Returns the post-processing effects of a camera."""
    bl_idname = 'LNCameraGetNode'
    bl_label = 'Get Camera Post Process'
    arm_version = 1

    def init(self, context):
        super(CameraGetNode, self).init(context)
        self.add_output('NodeSocketFloat', 'F-Stop')
        self.add_output('NodeSocketFloat', 'Shutter Time')
        self.add_output('NodeSocketFloat', 'ISO')
        self.add_output('NodeSocketFloat', 'Exposure Compensation')
        self.add_output('NodeSocketFloat', 'Fisheye Distortion')
        self.add_output('NodeSocketBool', 'Auto Focus')
        self.add_output('NodeSocketFloat', 'DOF Distance')
        self.add_output('NodeSocketFloat', 'DOF Length')
        self.add_output('NodeSocketFloat', 'DOF F-Stop')
        self.add_output('NodeSocketFloat', 'Film Grain')
