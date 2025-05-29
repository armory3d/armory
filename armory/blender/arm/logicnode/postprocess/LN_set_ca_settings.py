from arm.logicnode.arm_nodes import *

class ChromaticAberrationSetNode(ArmLogicTreeNode):
    """Set the chromatic aberration post-processing settings.
    Type: Simple 0 Spectral 1.
    """
    bl_idname = 'LNChromaticAberrationSetNode'
    bl_label = 'Set CA Settings'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Strength', default_value=2.0)
        self.add_input('ArmIntSocket', 'Samples', default_value=32)
        self.add_input('ArmIntSocket', 'Type', default_value=0)

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
