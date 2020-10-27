from arm.logicnode.arm_nodes import *

class ChromaticAberrationSetNode(ArmLogicTreeNode):
    """Set the chromatic aberration post-processing settings."""
    bl_idname = 'LNChromaticAberrationSetNode'
    bl_label = 'Set CA Settings'
    arm_version = 1

    def init(self, context):
        super(ChromaticAberrationSetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Strength', default_value=2.0)
        self.add_input('NodeSocketInt', 'Samples', default_value=32)
        self.add_output('ArmNodeSocketAction', 'Out')
