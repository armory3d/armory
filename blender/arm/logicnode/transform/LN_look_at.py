from arm.logicnode.arm_nodes import *

class LookAtNode(ArmLogicTreeNode):
    """Returns *a* rotation that makes something look away from X,Y or Z, and instead look in the 'from->to' direction"""
    bl_idname = 'LNLookAtNode'
    bl_label = 'Look At'
    arm_section = 'rotation'
    arm_version = 2

    property0: HaxeEnumProperty(
        'property0',
        items = [('X', ' X', 'X'),
                 ('-X', '-X', '-X'),
                 ('Y', ' Y', 'Y'),
                 ('-Y', '-Y', '-Y'),
                 ('Z', ' Z', 'Z'),
                 ('-Z', '-Z', '-Z')],
        name='With', default='Z')

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'From Location')
        self.add_input('ArmVectorSocket', 'To Location')

        self.add_output('ArmRotationSocket', 'Rotation')

        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')


    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        
        # transition from version 1 to version 2: make rotations their own sockets
        # this transition is a mess, I know.    
        newself = self.id_data.nodes.new('LNLookAtNode')
        converter = self.id_data.nodes.new('LNSeparateRotationNode')
        self.id_data.links.new(newself.outputs[0], converter.inputs[0])
        converter.property0 = 'EulerAngles'
        converter.property1 = 'Rad'
        converter.property2 = 'XZY'
        for link in self.outputs[0].links:
            self.id_data.links.new(converter.outputs[0], link.to_socket)

        return [newself, converter]
