from arm.logicnode.arm_nodes import *

class ChromaticAberrationGetNode(ArmLogicTreeNode):
    """Returns the chromatic aberration post-processing settings."""
    bl_idname = 'LNChromaticAberrationGetNode'
    bl_label = 'Get CA Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Strength')
        self.add_output('ArmFloatSocket', 'Samples')
