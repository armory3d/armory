from arm.logicnode.arm_nodes import *


@deprecated('Set Cursor State')
class ShowMouseNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use the 'Set Cursor State' node instead."""
    bl_idname = 'LNShowMouseNode'
    bl_label = "Set Mouse Visible"
    bl_description = "Please use the \"Set Cursor State\" node instead"
    arm_category = 'Input'
    arm_section = 'mouse'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Show')
        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        if len(self.inputs[1].links) == 0:
            # if the value is 'hard-coded', then use a simple replacement. Otherwise, use a Not node.
            return NodeReplacement(
                'LNShowMouseNode', self.arm_version, 'LNSetCursorStateNode', 1,
                in_socket_mapping={0:0}, out_socket_mapping={0:0},  # deliberately forgetting input 1 here: it is taken care of in the next line
                input_defaults={1: not self.inputs[1].default_value},
                property_defaults={'property0': 'Hide'}
            )

        new_main = node_tree.nodes.new('LNSetCursorStateNode')
        new_secondary = node_tree.nodes.new('LNNotNode')
        new_main.property0 = 'Hide'

        node_tree.links.new(self.inputs[0].links[0].from_socket, new_main.inputs[0])  # Action in
        node_tree.links.new(self.inputs[1].links[0].from_socket, new_secondary.inputs[0])  # Value in
        node_tree.links.new(new_secondary.outputs[0], new_main.inputs[1])  # Value in, part 2

        for link in self.outputs[0].links:
            node_tree.links.new(new_main.outputs[0], link.to_socket)  # Action out

        return [new_main, new_secondary]
