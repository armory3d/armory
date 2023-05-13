from arm.logicnode.arm_nodes import *

class SetActionSpeedNode(ArmLogicTreeNode):
    """Sets the current action playback speed of the given object."""
    bl_idname = 'LNSetActionSpeedNode'
    bl_label = 'Set Action Speed'
    bl_width_default = 200
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action ID')
        self.add_input('ArmFloatSocket', 'Speed', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNSetActionSpeedNode', self.arm_version, 'LNSetActionSpeedNode', 2,
            in_socket_mapping={}, out_socket_mapping={}
        )
