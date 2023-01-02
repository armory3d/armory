from arm.logicnode.arm_nodes import *


class BloomGetNode(ArmLogicTreeNode):
    """Return the current bloom post-processing settings. This node
    requires `Armory Render Path > Renderer > Realtime postprocess`
    to be enabled in order to work.
    """
    bl_idname = 'LNBloomGetNode'
    bl_label = 'Get Bloom Settings'
    arm_version = 2

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Threshold')
        self.add_output('ArmFloatSocket', 'Knee')
        self.add_output('ArmFloatSocket', 'Strength')
        self.add_output('ArmFloatSocket', 'Radius')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        return NodeReplacement(
            'LNBloomGetNode', 1,
            'LNBloomGetNode', 2,
            {}, {0: 0, 1: 2, 2: 3}
        )
