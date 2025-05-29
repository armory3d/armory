from arm.logicnode.arm_nodes import *

class ChromaticAberrationGetNode(ArmLogicTreeNode):
    """Returns the chromatic aberration post-processing settings.
    Type: Simple 0 Spectral 1.
    """
    bl_idname = 'LNChromaticAberrationGetNode'
    bl_label = 'Get CA Settings'
    arm_version = 2

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Strength')
        self.add_output('ArmFloatSocket', 'Samples')
        self.add_output('ArmIntSocket', 'Type')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
