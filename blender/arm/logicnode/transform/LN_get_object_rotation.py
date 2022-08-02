from arm.logicnode.arm_nodes import *

class GetRotationNode(ArmLogicTreeNode):
    """Returns the current rotation of the given object."""
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Object Rotation'
    arm_section = 'rotation'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmRotationSocket', 'Rotation')
        

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    property0: HaxeEnumProperty(
        'property0',
        items = [('Local', 'Local', 'Local'),
                 ('Global', 'Global', 'Global')],
        name='', default='Local')


    
    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        
        # transition from version 1 to version 2: make rotations their own sockets
        # this transition is a mess, I know.

        newself = self.id_data.nodes.new('LNGetRotationNode')
        newself.property0 = 'Local'
        newnodes = [newself]

        if len(self.outputs[0].links)>0:
            # euler (radians) needed
            converter = self.id_data.nodes.new('LNSeparateRotationNode')
            converter.property0 = "EulerAngles"
            converter.property1 = "Rad"
            converter.property2 = "XZY"
            newnodes.append(converter)
            self.id_data.links.new(newself.outputs[0], converter.inputs[0])
            for link in self.outputs[0].links:
                self.id_data.links.new(converter.outputs[0], link.to_socket)

        if len(self.outputs[4].links)>0 or len(self.outputs[5].links)>0:
            # quaternion needed
            converter = self.id_data.nodes.new('LNSeparateRotationNode')
            converter.property0 = "Quaternion"
            newnodes.append(converter)
            self.id_data.links.new(newself.outputs[0], converter.inputs[0])
            for link in self.outputs[4].links:
                self.id_data.links.new(converter.outputs[0], link.to_socket)
            for link in self.outputs[5].links:
                self.id_data.links.new(converter.outputs[1], link.to_socket)

        if len(self.outputs[1].links)>0 or len(self.outputs[2].links)>0 or len(self.outputs[3].links)>0:
            # axis/angle needed
            converter = self.id_data.nodes.new('LNSeparateRotationNode')
            converter.property0 = "AxisAngle"
            converter.property1 = "Rad"
            newnodes.append(converter)
            self.id_data.links.new(newself.outputs[0], converter.inputs[0])
            for link in self.outputs[1].links:
                self.id_data.links.new(converter.outputs[0], link.to_socket)

            if len(self.outputs[3].links)==0 and len(self.outputs[2].links)==0:
                pass
            elif len(self.outputs[3].links)==0:
                for link in self.outputs[2].links:
                    self.id_data.links.new(converter.outputs[1], link.to_socket)
            elif len(self.outputs[2].links)==0:
                converter.property1 = 'Deg'
                for link in self.outputs[3].links:
                    self.id_data.links.new(converter.outputs[1], link.to_socket)
            else:
                for link in self.outputs[2].links:
                    self.id_data.links.new(converter.outputs[1], link.to_socket)
                converter = self.id_data.nodes.new('LNSeparateRotationNode')
                converter.property0 = "AxisAngle"
                converter.property1 = "Deg"
                converter.property2 = "XYZ"  # bogus
                newnodes.append(converter)
                self.id_data.links.new(newself.outputs[0], converter.inputs[0])
                for link in self.outputs[3].links:
                    self.id_data.links.new(converter.outputs[1], link.to_socket)
                
        return newnodes
