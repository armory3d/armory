from arm.logicnode.arm_nodes import *

class CameraGetNode(ArmLogicTreeNode):
    """Get postprocessing effects of the camera."""
    bl_idname = 'LNCameraGetNode'
    bl_label = 'Get Camera Postprocessing'

    def init(self, context):
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

add_node(CameraGetNode, category=PKG_AS_CATEGORY)
