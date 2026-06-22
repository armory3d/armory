from arm.logicnode.arm_nodes import *

class SeparateTransformNode(ArmLogicTreeNode):
    """Separates the transform of the given object."""
    bl_idname = 'LNSeparateTransformNode'
    bl_label = 'Separate Transform'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmVectorSocket', 'Location')
        self.add_output('ArmRotationSocket', 'Rotation')
        self.add_output('ArmVectorSocket', 'Scale')



    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        
        # transition from version 1 to version 2: make rotations their own sockets
        # this transition is a mess, I know.    
        newself = self.id_data.nodes.new('LNSeparateTransformNode')
        for link in self.outputs[0].links:
            self.id_data.links.new(newself.outputs[0], link.to_socket)
        for link in self.outputs[2].links:
            self.id_data.links.new(newself.outputs[2], link.to_socket)
        for link in self.inputs[0].links:
            self.id_data.links.new(link.from_socket, newself.inputs[0])

        ret = [newself]
        rot_links = self.outputs[1].links
        if len(rot_links) >0:
            converter = self.id_data.nodes.new('LNSeparateRotationNode')
            ret.append(converter)
            self.id_data.links.new(newself.outputs[1], converter.inputs[0])
            converter.property0 = 'EulerAngles'
            converter.property1 = 'Rad'
            converter.property2 = 'XZY'
            for link in rot_links:
                self.id_data.links.new(converter.outputs[0], link.to_socket)
            
        return ret
