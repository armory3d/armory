from arm.logicnode.arm_nodes import *

class LetterboxSetNode(ArmLogicTreeNode):
    """Set the letterbox post-processing settings."""
    bl_idname = 'LNLetterboxSetNode'
    bl_label = 'Set Letterbox Settings'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmColorSocket', 'Color', default_value=[0.0, 0.0, 0.0, 1.0])
        self.add_input('ArmFloatSocket', 'Size', default_value=0.1)

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
