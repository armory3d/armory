import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMouseLockNode(ArmLogicTreeNode):
    bl_idname = 'LNGetMouseLockNode'
    bl_label = 'Get Mouse Lock (Depreciated)'
    bl_description = "Please use the \"Get Cursor State\" node instead"
    bl_icon = 'ERROR'
    arm_version = 2

    def init(self, context):
        super(GetMouseLockNode, self).init(context)
        self.outputs.new('NodeSocketBool', 'Is Locked')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNGetMouseLockNode', self.arm_version, 'LNGetCursorStateNode', 1,
            in_socket_mapping = {}, out_socket_mapping={0:2}
        )

add_node(GetMouseLockNode, category='input', section='mouse', is_obsolete=True)
