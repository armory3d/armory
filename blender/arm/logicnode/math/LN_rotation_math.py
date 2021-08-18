from arm.logicnode.arm_nodes import *
from mathutils import Vector

class RotationMathNode(ArmLogicTreeNode):
    """Mathematical operations on rotations."""
    bl_idname = 'LNRotationMathNode'
    bl_label = 'Rotation Math'
    bl_description = 'Mathematical operations that can be performed on rotations, no matter their internal representation'
    arm_section = 'quaternions'
    arm_version = 1


    @staticmethod    
    def get_count_in(operation_name):
        return {
            'Inverse': 1,
            'Normalize': 1,
            'Compose': 2,
            'Amplify': 2,
            'FromTo': 2,
            #'FromRotationMat': 2,
            'Lerp': 3,
            'Slerp': 3,
        }.get(operation_name, 0)

    def ensure_input_socket(self, socket_number, newclass, newname):
        while len(self.inputs) < socket_number:
            self.inputs.new('ArmFloatSocket', 'BOGUS')
        if len(self.inputs) > socket_number:
            if len(self.inputs[socket_number].links) == 1:
                source_socket = self.inputs[socket_number].links[0].from_socket
            else:    
                source_socket = None
            self.inputs.remove(self.inputs[socket_number])
        else:
            source_socket = None
        
            
        self.inputs.new(newclass, newname)
        self.inputs.move(len(self.inputs)-1, socket_number)
        if source_socket is not None:
            self.id_data.links.new(source_socket, self.inputs[socket_number])
        
    def ensure_output_socket(self, socket_number, newclass, newname):
        sink_sockets = []
        while len(self.outputs) < socket_number:
            self.outputs.new('ArmFloatSocket', 'BOGUS')
        if len(self.outputs) > socket_number:
            for link in self.inputs[socket_number].links:
                sink_sockets.append(link.to_socket)
            self.inputs.remove(self.inputs[socket_number])

        self.inputs.new(newclass, newname)
        self.inputs.move(len(self.inputs)-1, socket_number)
        for socket in sink_sockets:
            self.id_data.links.new(self.inputs[socket_number], socket)

    def on_property_update(self, context):
        # Checking the selection of another operation


        # Rotation as argument 0:
        if self.property0 in ('Inverse','Normalize','Amplify'):
            self.ensure_input_socket(0, "ArmRotationSocket", "Rotation")
            self.ensure_input_socket(1, "ArmFloatSocket", "Amplification factor")
        elif self.property0 in ('Slerp','Lerp','Compose'):
            self.ensure_input_socket(0, "ArmRotationSocket", "From")
            self.ensure_input_socket(1, "ArmRotationSocket", "To")

            if self.property0 == 'Compose':
                self.inputs[0].name = 'Outer rotation'
                self.inputs[1].name = 'Inner rotation'
            else:
                self.ensure_input_socket(2, "ArmFloatSocket", "Interpolation factor")

        elif self.property0 == 'FromTo':
            self.ensure_input_socket(0, "ArmVectorSocket", "From")
            self.ensure_input_socket(1, "ArmVectorSocket", "To")
            
        # Rotation as argument 1:
        if self.property0 in ('Compose','Lerp','Slerp'):
            if self.inputs[1].bl_idname != "ArmRotationSocket":
                self.replace_input_socket(1, "ArmRotationSocket", "Rotation 2")
                if self.property0 == 'Compose':
                    self.inputs[1].name = "Inner quaternion"
        # Float as argument 1:
        if self.property0 == 'Amplify':
            if self.inputs[1].bl_idname != 'ArmFloatSocket':
                self.replace_input_socket(1, "ArmFloatSocket", "Amplification factor")
        # Vector as argument 1:
        #if self.property0 == 'FromRotationMat':
        #    # WHAT??
        #    pass

        while len(self.inputs) > self.get_count_in(self.property0):
            self.inputs.remove(self.inputs[len(self.inputs)-1])
        

    property0: HaxeEnumProperty(
        'property0',
        items = [('Compose', 'Compose (multiply)', 'compose (multiply) two rotations. Note that order of the composition matters.'),
                 ('Amplify', 'Amplify (multiply by float)', 'Amplify or diminish the effect of a rotation'),
                 #('Normalize', 'Normalize', 'Normalize'),
                 ('Inverse', 'Get Inverse', 'from r, get the rotation r2 so that " r×r2=r2×r= <no rotation>" '),
                 ('Lerp', 'Lerp', 'Linearly interpolation'),
                 ('Slerp', 'Slerp', 'Spherical linear interpolation'),
                 ('FromTo', 'From To', 'From direction To direction'),
                 #('FromRotationMat', 'From Rotation Mat', 'From Rotation Mat')
                 ],
        name='', default='Compose', update=on_property_update)

    #def __init__(self):    
    #    array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmRotationSocket', 'Outer rotation', default_value=(0.0, 0.0, 0.0, 1.0) )
        self.add_input('ArmRotationSocket', 'Inner rotation', default_value=(0.0, 0.0, 0.0, 1.0) )
        self.add_output('ArmRotationSocket', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0') # Operation
