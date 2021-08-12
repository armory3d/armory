from arm.logicnode.arm_nodes import *
from arm.logicnode.arm_sockets import ArmRotationSocket as Rotation

class RotateObjectNode(ArmLogicTreeNode):
    """Rotates the given object."""
    bl_idname = 'LNRotateObjectNode'
    bl_label = 'Rotate Object'
    arm_section = 'rotation'
    arm_version = 2

    def init(self, context):
        super().init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketRotation', 'Rotation')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    property0: EnumProperty(
        items = [('Local', 'Local F.O.R.', 'Frame of reference oriented with the object'),
                 ('Global', 'Global/Parent F.O.R.',
                  'Frame of reference oriented with the object\'s parent or the world')],
        name='', default='Local')







    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        
        # transition from version 1 to version 2: make rotations their own sockets
        # this transition is a mess, I know.

        newself = self.id_data.nodes.new('LNRotateObjectNode')
        inputnode = self.id_data.nodes.new('LNRotationNode')
        self.id_data.links.new(inputnode.outputs[0], newself.inputs[2])
        newself.inputs[1].default_value_raw = self.inputs[1].default_value_raw
        inputnode.inputs[0].default_value = self.inputs[2].default_value
        inputnode.inputs[1].default_value = self.inputs[3].default_value

        if len(self.inputs[0].links) >0:
            self.id_data.links.new(self.inputs[0].links[0].from_socket, newself.inputs[0])
        if len(self.inputs[1].links) >0:
            self.id_data.links.new(self.inputs[1].links[0].from_socket, newself.inputs[1])
        if len(self.inputs[2].links) >0:
            self.id_data.links.new(self.inputs[2].links[0].from_socket, inputnode.inputs[0])
        if len(self.inputs[3].links) >0:
            self.id_data.links.new(self.inputs[3].links[0].from_socket, inputnode.inputs[1])

        # first, convert the default value
        if self.property0 == 'Quaternion':
            inputnode.property0 = 'Quaternion'
        elif self.property0 == 'Euler Angles':
            inputnode.property0 = 'EulerAngles'
            inputnode.property1 = 'Rad'
            inputnode.property2 = 'XZY'  # legacy order
        else:  # starts with "Angle Axies"
            inputnode.property0 = 'AxisAngle'
            if 'Degrees' in self.property0:
                inputnode.property1 = 'Deg'
            else:
                inputnode.property1 = 'Rad'
        quat = Rotation.convert_to_quaternion(
            self.inputs[2].default_value,
            self.inputs[3].default_value,
            inputnode.property0,
            inputnode.property1,
            inputnode.property2
        )
        newself.inputs[2].default_value_raw = quat
        return [newself, inputnode]
