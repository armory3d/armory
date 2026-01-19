from arm.logicnode.arm_nodes import *

class SetTilesheetNode(ArmLogicTreeNode):
    """Sets the tilesheet action for the given object."""
    bl_idname = 'LNSetTilesheetNode'
    bl_label = 'Set Tilesheet'
    arm_version = 2
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version != 1:
            raise LookupError()

        return NodeReplacement(
            'LNSetTilesheetNode', self.arm_version, 'LNSetTilesheetNode', 2,
            in_socket_mapping={0: 0, 1: 1, 3: 2}, out_socket_mapping={0: 0}
        )