from arm.logicnode.arm_nodes import *

class SetActionPausedNode(ArmLogicTreeNode):
    """Sets the action paused state of the given object."""
    bl_idname = 'LNSetActionPausedNode'
    bl_label = 'Set Action Paused'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action ID')
        self.add_input('ArmBoolSocket', 'Paused')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNSetActionPausedNode', self.arm_version, 'LNSetActionPausedNode', 2,
            in_socket_mapping={}, out_socket_mapping={}
        )
