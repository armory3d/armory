from arm.logicnode.arm_nodes import *

class BlendActionNode(ArmLogicTreeNode):
    """Interpolates between the two given actions."""
    bl_idname = 'LNBlendActionNode'
    bl_label = 'Blend Action'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimTree', 'Action 1')
        self.add_input('ArmNodeSocketAnimTree', 'Action 2')
        self.add_input('ArmFactorSocket', 'Factor', default_value = 0.5)
        self.add_input('ArmIntSocket', 'Bone Group', default_value = -1)

        self.add_output('ArmNodeSocketAnimTree', 'Result')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNBlendActionNode', self.arm_version, 'LNBlendActionNode', 2,
            in_socket_mapping={}, out_socket_mapping={}
        )