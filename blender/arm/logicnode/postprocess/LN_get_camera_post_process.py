from arm.logicnode.arm_nodes import *

class CameraGetNode(ArmLogicTreeNode):
    """Returns the post-processing effects of a camera."""
    bl_idname = 'LNCameraGetNode'
    bl_label = 'Get Camera Post Process'
    arm_version = 4

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'F-Stop')#0
        self.add_output('ArmFloatSocket', 'Shutter Time')#1
        self.add_output('ArmFloatSocket', 'ISO')#2
        self.add_output('ArmFloatSocket', 'Exposure Compensation')#3
        self.add_output('ArmFloatSocket', 'Fisheye Distortion')#4
        self.add_output('ArmBoolSocket', 'Auto Focus')#5
        self.add_output('ArmFloatSocket', 'DOF Distance')#6
        self.add_output('ArmFloatSocket', 'DOF Length')#7
        self.add_output('ArmFloatSocket', 'DOF F-Stop')#8
        self.add_output('ArmBoolSocket', 'Tonemapping')#9
        self.add_output('ArmFloatSocket', 'Distort')#10
        self.add_output('ArmFloatSocket', 'Film Grain')#11
        self.add_output('ArmFloatSocket', 'Sharpen')#12
        self.add_output('ArmFloatSocket', 'Vignette')#13

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 3):
           raise LookupError()
            
        return NodeReplacement.Identity(self)
