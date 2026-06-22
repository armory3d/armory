from arm.logicnode.arm_nodes import *


@deprecated('Set Cursor State')
class SetMouseLockNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use the 'Set Cursor State' node instead."""
    bl_idname = 'LNSetMouseLockNode'
    bl_label = 'Set Mouse Lock'
    bl_description = "Please use the \"Set Cursor State\" node instead"
    arm_category = 'Input'
    arm_section = 'mouse'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Lock')
        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNSetMouseLockNode', self.arm_version, 'LNSetCursorStateNode', 1,
            in_socket_mapping = {0:0, 1:1}, out_socket_mapping={0:0},
            property_defaults={'property0': "Lock"}
        )
