from arm.logicnode.arm_nodes import *

class PlayActionFromNode(ArmLogicTreeNode):
    """Plays action starting from the given frame."""
    bl_idname = 'LNPlayActionFromNode'
    bl_label = 'Play Action From'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_input('ArmIntSocket', 'Start Frame')
        self.add_input('ArmFloatSocket', 'Blend', default_value = 0.25)
        self.add_input('ArmFloatSocket', 'Speed', default_value = 1.0)
        self.add_input('ArmBoolSocket', 'Loop', default_value = False)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNPlayActionFromNode', self.arm_version, 'LNPlayActionFromNode', 2,
            in_socket_mapping={0:0, 1:1, 2:2, 3:3, 4:4}, out_socket_mapping={0:0, 1:1}
        )
