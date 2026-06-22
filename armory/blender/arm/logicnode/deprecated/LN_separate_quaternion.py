from arm.logicnode.arm_nodes import *


@deprecated(message='Do not use quaternion sockets')
class SeparateQuaternionNode(ArmLogicTreeNode):
    """Splits the given quaternion into X, Y, Z and W."""
    bl_idname = 'LNSeparateQuaternionNode'
    bl_label = "Separate Quaternion (do not use: quaternions sockets have been phased out entirely)"
    bl_description = "Separate a quaternion object (transported through a vector socket) into its four compoents."
    arm_category = 'Math'
    arm_section = 'quaternions'
    arm_version = 2  # deprecate

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Quaternion')

        self.add_output('ArmFloatSocket', 'X')
        self.add_output('ArmFloatSocket', 'Y')
        self.add_output('ArmFloatSocket', 'Z')
        self.add_output('ArmFloatSocket', 'W')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        # transition from version 1 to version 2[deprecated]
        newself = node_tree.nodes.new('LNSeparateRotationNode')
        separator = node_tree.nodes.new('LNSeparateVectorNode')

        newself.property0 = 'Quaternion'
        newself.property1 = 'Rad'  # bogus
        newself.property2 = 'XYZ'  # bogus

        for link in self.inputs[0].links:
            node_tree.links.new(link.from_socket, newself.inputs[0])
        node_tree.links.new(newself.outputs[0], separator.inputs[0])
        for link in self.outputs[0].links:
            node_tree.links.new(separator.outputs[0], link.to_socket)
        for link in self.outputs[1].links:
            node_tree.links.new(separator.outputs[1], link.to_socket)
        for link in self.outputs[2].links:
            node_tree.links.new(separator.outputs[2], link.to_socket)
        for link in self.outputs[3].links:
            node_tree.links.new(newself.outputs[1], link.to_socket)
        return [newself, separator]
