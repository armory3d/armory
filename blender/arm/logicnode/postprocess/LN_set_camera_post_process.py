from arm.logicnode.arm_nodes import *

class CameraSetNode(ArmLogicTreeNode):
    """Set the post-processing effects of a camera."""
    bl_idname = 'LNCameraSetNode'
    bl_label = 'Set Camera Post Process'
    arm_version = 1

    def init(self, context):
        super(CameraSetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'F-stop', default_value=2.0)
        self.add_input('NodeSocketFloat', 'Shutter Time', default_value=1.0)
        self.add_input('NodeSocketFloat', 'ISO', default_value=100.0)
        self.add_input('NodeSocketFloat', 'Exposure Compensation', default_value=0.0)
        self.add_input('NodeSocketFloat', 'Fisheye Distortion', default_value=0.01)
        self.add_input('NodeSocketBool', 'Auto Focus', default_value=True)
        self.add_input('NodeSocketFloat', 'DoF Distance', default_value=10.0)
        self.add_input('NodeSocketFloat', 'DoF Length', default_value=160.0)
        self.add_input('NodeSocketFloat', 'DoF F-Stop', default_value=128.0)
        self.add_input('NodeSocketInt', 'Tonemapper', default_value=0.0)
        self.add_input('NodeSocketFloat', 'Film Grain', default_value=2.0)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CameraSetNode, category=PKG_AS_CATEGORY)
