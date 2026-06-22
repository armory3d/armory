from arm.logicnode.arm_nodes import *

class SetCameraScaleNode(ArmLogicTreeNode):
    """Sets the aspect of the given camera."""
    bl_idname = 'LNSetCameraScaleNode'
    bl_label = 'Set Camera Ortho Scale'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmFloatSocket', 'Ortho Scale', default_value=1.7)

        self.add_output('ArmNodeSocketAction', 'Out')
