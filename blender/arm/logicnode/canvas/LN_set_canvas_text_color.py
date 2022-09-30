from arm.logicnode.arm_nodes import *
import arm.node_utils as node_utils


@deprecated('Set Canvas Color')
class CanvasSetTextColorNode(ArmLogicTreeNode):
    """Sets the text color of the given UI element."""
    bl_idname = 'LNCanvasSetTextColorNode'
    bl_label = 'Set Canvas Text Color'
    arm_version = 2
    arm_category = 'Canvas'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmFloatSocket', 'R')
        self.add_input('ArmFloatSocket', 'G')
        self.add_input('ArmFloatSocket', 'B')
        self.add_input('ArmFloatSocket', 'A')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        newnode = node_tree.nodes.new('LNCanvasSetColorNode')
        newnode.property0 = 'color_text'

        for link in self.inputs[0].links:
            node_tree.links.new(link.from_socket, newnode.inputs[0])

        if self.inputs[1].is_linked:
            for link in self.inputs[1].links:
                node_tree.links.new(link.from_socket, newnode.inputs[1])
        else:
            node_utils.set_socket_default(newnode.inputs[1], node_utils.get_socket_default(self.inputs[1]))

        # We do not have a RGBA to Color node or a Vec4 node currently,
        # so we cannot reconnect color inputs... So unfortunately we can only
        # use the socket default colors here
        newnode.inputs[2].default_value_raw[0] = self.inputs[2].default_value_raw
        newnode.inputs[2].default_value_raw[1] = self.inputs[3].default_value_raw
        newnode.inputs[2].default_value_raw[2] = self.inputs[4].default_value_raw
        newnode.inputs[2].default_value_raw[3] = self.inputs[5].default_value_raw

        return newnode
