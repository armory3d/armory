from arm.logicnode.arm_nodes import *

class SetCameraAspectNode(ArmLogicTreeNode):
    """Sets the aspect of the given camera."""
    bl_idname = 'LNSetCameraAspectNode'
    bl_label = 'Set Camera Aspect'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmFloatSocket', 'Aspect', default_value=1.7)

        self.add_output('ArmNodeSocketAction', 'Out')
