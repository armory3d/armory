from arm.logicnode.arm_nodes import *


class TransformNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the location, rotation and scale values as a transform."""
    bl_idname = 'LNTransformNode'
    bl_label = 'Transform'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Location')
        self.add_input('ArmRotationSocket', 'Rotation')
        self.add_input('ArmVectorSocket', 'Scale', default_value=[1.0, 1.0, 1.0])
        self.add_output('ArmDynamicSocket', 'Transform', is_var=True)

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.inputs[0].default_value_raw = master_node.inputs[0].get_default_value()
        self.inputs[2].default_value_raw = master_node.inputs[2].get_default_value()

        self.inputs[1].default_value_mode = master_node.inputs[1].default_value_mode
        self.inputs[1].default_value_unit = master_node.inputs[1].default_value_unit
        self.inputs[1].default_value_order = master_node.inputs[1].default_value_order
        self.inputs[1].default_value_s0 = master_node.inputs[1].default_value_s0
        self.inputs[1].default_value_s1 = master_node.inputs[1].default_value_s1
        self.inputs[1].default_value_s2 = master_node.inputs[1].default_value_s2
        self.inputs[1].default_value_s3 = master_node.inputs[1].default_value_s3

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()


        # transition from version 1 to version 2: make rotations their own sockets
        # this transition is a mess, I know.
        newself = self.id_data.nodes.new('LNTransformNode')
        ret = [newself]

        for link in self.inputs[0].links:
            self.id_data.links.new(link.from_socket, newself.inputs[0])
        for link in self.inputs[2].links:
            self.id_data.links.new(link.from_socket, newself.inputs[2])
        for link in self.outputs[0].links:
            self.id_data.links.new(newself.outputs[0], link.to_socket)

        links_rot = self.inputs[1].links
        if len(links_rot) > 0:
            converter = self.id_data.nodes.new('LNRotationNode')
            self.id_data.links.new(converter.outputs[0], newself.inputs[1])
            converter.property0 = 'EulerAngles'
            converter.property1 = 'Rad'
            converter.property2 = 'XZY'
            ret.append(converter)
            for link in links_rot:
                self.id_data.links.new(link.from_socket, converter.inputs[0])

        return ret
