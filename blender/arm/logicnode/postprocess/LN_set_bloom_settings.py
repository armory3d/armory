from arm.logicnode.arm_nodes import *
import arm.node_utils


class BloomSetNode(ArmLogicTreeNode):
    """Set the bloom post-processing settings. This node
    requires `Armory Render Path > Renderer > Realtime postprocess`
    to be enabled in order to work.
    """
    bl_idname = 'LNBloomSetNode'
    bl_label = 'Set Bloom Settings'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Threshold', default_value=0.8)
        self.add_input('ArmFloatSocket', 'Knee', default_value=0.5)
        self.add_input('ArmFloatSocket', 'Strength', default_value=0.05)
        self.add_input('ArmFloatSocket', 'Radius', default_value=6.5)

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        return NodeReplacement(
            'LNBloomSetNode', 1,
            'LNBloomSetNode', 2,
            {0: 0, 1: 1, 2: 3, 3: 4}, {0: 0},
            None,
            {
                1: arm.node_utils.get_socket_default(self.inputs[1]),
                3: arm.node_utils.get_socket_default(self.inputs[2]),
                4: arm.node_utils.get_socket_default(self.inputs[3]),
            }
        )
