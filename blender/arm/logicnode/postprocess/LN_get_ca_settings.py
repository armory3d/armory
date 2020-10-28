from arm.logicnode.arm_nodes import *

class ChromaticAberrationGetNode(ArmLogicTreeNode):
    """Returns the chromatic aberration post-processing settings."""
    bl_idname = 'LNChromaticAberrationGetNode'
    bl_label = 'Get CA Settings'
    arm_version = 1

    def init(self, context):
        super(ChromaticAberrationGetNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Strength')
        self.add_output('NodeSocketFloat', 'Samples')
