import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *


@deprecated('Get Cursor State')
class GetMouseLockNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use the 'Get Cursor State' node instead."""
    bl_idname = 'LNGetMouseLockNode'
    bl_label = 'Get Mouse Lock'
    bl_description = "Please use the \"Get Cursor State\" node instead"
    arm_version = 2
    arm_category = 'Input'
    arm_section = 'mouse'

    def arm_init(self, context):
        self.outputs.new('ArmBoolSocket', 'Is Locked')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNGetMouseLockNode', self.arm_version, 'LNGetCursorStateNode', 1,
            in_socket_mapping={}, out_socket_mapping={0: 2}
        )
