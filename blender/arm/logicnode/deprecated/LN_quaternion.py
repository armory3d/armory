from arm.logicnode.arm_nodes import *
from mathutils import Vector


@deprecated(message='Do not use quaternion sockets')
class QuaternionNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNQuaternionNode'
    bl_label = 'Quaternion'
    bl_description = 'Create a quaternion variable (transported through a vector socket)'
    arm_category = 'Variable'
    arm_section = 'quaternions'
    arm_version = 2  # deprecate

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Z')
        self.add_input('ArmFloatSocket', 'W', default_value=1.0)

        self.add_output('ArmVectorSocket', 'Quaternion')
        self.add_output('ArmVectorSocket', 'XYZ')
        self.add_output('ArmVectorSocket', 'W')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        # transition from version 1 to version 2[deprecated]

        newnodes = []

        rawlinks = self.outputs[0].links
        xyzlinks = self.outputs[1].links
        wlinks = self.outputs[2].links
        if len(rawlinks)>0 or len(xyzlinks)>0:
            xyzcomb = node_tree.nodes.new('LNVectorNode')
            newnodes.append(xyzcomb)

            xyzcomb.inputs[0].default_value = self.inputs[0].default_value
            xyzcomb.inputs[1].default_value = self.inputs[1].default_value
            xyzcomb.inputs[2].default_value = self.inputs[2].default_value
            for link in self.inputs[0].links:
                node_tree.links.new(link.from_socket, xyzcomb.inputs[0])
            for link in self.inputs[1].links:
                node_tree.links.new(link.from_socket, xyzcomb.inputs[1])
            for link in self.inputs[2].links:
                node_tree.links.new(link.from_socket, xyzcomb.inputs[2])

            for link in xyzlinks:
                node_tree.links.new(xyzcomb.outputs[0], link.to_socket)
            if len(rawlinks)>0:
                rotnode = node_tree.nodes.new('LNRotationNode')
                newnodes.append(rotnode)
                rotnode.property0 = 'Quaternion'
                rotnode.inputs[0].default_value = Vector(
                    (self.inputs[0].default_value,
                     self.inputs[1].default_value,
                     self.inputs[2].default_value))
                rotnode.inputs[1].default_value = self.inputs[3].default_value
                node_tree.links.new(xyzcomb.outputs[0], rotnode.inputs[0])
                for link in self.inputs[3].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, rotnode.inputs[1])
                for link in rawlinks:
                    node_tree.links.new(rotnode.outputs[0], link.to_socket)

        if len(self.inputs[3].links)>0:
            fromval = self.inputs[3].links[0].from_socket
            for link in self.outputs[2].links:
                node_tree.links.new(fromval, link.to_socket)
        else:
            for link in self.outputs[2].links:
                link.to_socket.default_value = self.inputs[3].default_value

        return newnodes
