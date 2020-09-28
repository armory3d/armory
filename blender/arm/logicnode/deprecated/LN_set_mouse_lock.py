from arm.logicnode.arm_nodes import *

class SetMouseLockNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use the 'Set Cursor State' node instead."""
    bl_idname = 'LNSetMouseLockNode'
    bl_label = 'Set Mouse Lock (Deprecated)'
    bl_description = "Please use the \"Set Cursor State\" node instead"
    bl_icon = 'ERROR'
    arm_version = 2

    def init(self, context):
        super(SetMouseLockNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Lock')
        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNSetMouseLockNode', self.arm_version, 'LNSetCursorStateNode', 1,
            in_socket_mapping = {0:0, 1:1}, out_socket_mapping={0:0},
            property_defaults={'property0': "Lock"}
        )

add_node(SetMouseLockNode, category='input', section='mouse', is_obsolete=True)
