from arm.logicnode.arm_nodes import *
import arm.node_utils as node_utils


@deprecated('Set Canvas Color')
class CanvasSetProgressBarColorNode(ArmLogicTreeNode):
    """Sets the color of the given UI element."""
    bl_idname = 'LNCanvasSetProgressBarColorNode'
    bl_label = 'Set Canvas Progress Bar Color'
    arm_version = 2
    arm_category = 'Canvas'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        newnode = node_tree.nodes.new('LNCanvasSetColorNode')
        newnode.property0 = 'color_progress'

        for link in self.inputs[0].links:
            node_tree.links.new(link.from_socket, newnode.inputs[0])

        if self.inputs[1].is_linked:
            for link in self.inputs[1].links:
                node_tree.links.new(link.from_socket, newnode.inputs[1])
        else:
            node_utils.set_socket_default(newnode.inputs[1], node_utils.get_socket_default(self.inputs[1]))

        if self.inputs[2].is_linked:
            for link in self.inputs[2].links:
                node_tree.links.new(link.from_socket, newnode.inputs[2])
        else:
            node_utils.set_socket_default(newnode.inputs[2], node_utils.get_socket_default(self.inputs[2]))

        return newnode
