import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *


@deprecated('Get Cursor State')
class GetMouseVisibleNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use the 'Get Cursor State' node instead."""
    bl_idname = 'LNGetMouseVisibleNode'
    bl_label = 'Get Mouse Visible'
    bl_description = "Please use the \"Get Cursor State\" node instead"
    arm_category = 'Input'
    arm_section = 'mouse'
    arm_version = 2

    def arm_init(self, context):
        self.outputs.new('ArmBoolSocket', 'Is Visible')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        mainnode = node_tree.nodes.new('LNGetCursorStateNode')
        secondnode = node_tree.nodes.new('LNNotNode')
        node_tree.links.new(mainnode.outputs[2], secondnode.inputs[0])
        for link in self.outputs[0].links:
            node_tree.links.new(secondnode.outputs[0], link.to_socket)

        return [mainnode, secondnode]
