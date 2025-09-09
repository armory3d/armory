from arm.logicnode.arm_nodes import *
from arm.logicnode.arm_sockets import ArmRotationSocket as Rotation

class QuaternionMathNode(ArmLogicTreeNode):
    """Mathematical operations on quaternions."""
    bl_idname = 'LNQuaternionMathNode'
    bl_label = 'Quaternion Math'
    bl_description = 'Mathematical operations that can be performed on rotations, when represented as quaternions specifically'
    arm_section = 'quaternions'
    arm_version = 3

    def ensure_input_socket(self, socket_number, newclass, newname, default_value=None):
        while len(self.inputs) < socket_number:
            self.inputs.new('ArmFloatSocket', 'BOGUS')
        if len(self.inputs) > socket_number:
            if len(self.inputs[socket_number].links) == 1:
                source_socket = self.inputs[socket_number].links[0].from_socket
            else:
                source_socket = None
            if (
                self.inputs[socket_number].bl_idname == newclass \
                and self.inputs[socket_number].arm_socket_type != 'NONE'
            ):
                default_value = self.inputs[socket_number].default_value_raw
            self.inputs.remove(self.inputs[socket_number])
        else:
            source_socket = None


        self.inputs.new(newclass, newname)
        if default_value != None:
            self.inputs[-1].default_value_raw = default_value
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

    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(operation_name):
        return {
            'Add': 0,
            'Subtract': 0,
            'DotProduct': 0,
            'Multiply': 0,
            'MultiplyFloats': 0,
            'Module': 1,
            'Normalize': 1,
            'GetEuler': 1,
            'FromTo': 2,
            'FromMat': 2,
            'FromRotationMat': 2,
            'ToAxisAngle': 2,
            'Lerp': 3,
            'Slerp': 3,
            'FromAxisAngle': 3,
            'FromEuler': 3
        }.get(operation_name, 0)

    def get_enum(self):
        return self.get('property0', 0)

    def set_enum(self, value):
        # Checking the selection of another operation
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0

        if select_current in ('Add','Subtract','Multiply','DotProduct') \
           and select_prev in ('Add','Subtract','Multiply','DotProduct'):
            pass  # same as select_current==select_prev for the sockets
        elif select_prev != select_current:
            if select_current in ('Add','Subtract','Multiply','DotProduct'):
                for i in range(  max(len(self.inputs)//2 ,2)  ):
                    self.ensure_input_socket(2*i, 'ArmVectorSocket', 'Quaternion %d XYZ'%i)
                    self.ensure_input_socket(2*i+1, 'ArmFloatSocket', 'Quaternion %d W'%i, default_value=1.0)
                if len(self.inputs)%1:
                    self.inputs.remove(self.inputs[len(self.inputs)-1])
            elif select_current == 'MultiplyFloats':
                self.ensure_input_socket(0, 'ArmVectorSocket', 'Quaternion XYZ')
                self.ensure_input_socket(1, 'ArmFloatSocket', 'Quaternion W', default_value=1.0)
                for i in range(  max(len(self.inputs)-2 ,1)  ):
                    self.ensure_input_socket(i+2, 'ArmFloatSocket', 'Value %d'%i)
            elif select_current in ('Module', 'Normalize'):
                self.ensure_input_socket(0, 'ArmVectorSocket', 'Quaternion XYZ')
                self.ensure_input_socket(1, 'ArmFloatSocket', 'Quaternion W', default_value=1.0)
                while len(self.inputs)>2:
                    self.inputs.remove(self.inputs[2])
            else:
                raise ValueError('Internal code of LNQuaternionMathNode failed to deal correctly with math operation "%s". Please report this to the developers.' %select_current)

        if select_current in ('Add','Subtract','Multiply','MultiplyFloats','Normalize'):
            self.outputs[0].name = 'XYZ Out'
            self.outputs[1].name = 'W Out'
        else:
            self.outputs[0].name = '[unused]'
            self.outputs[1].name = 'Value Out'

        self['property0'] = value
        self['property0_proxy'] = value


    # this property swaperoo is kinda janky-looking, but necessary.
    # Read more on LN_rotate_object.py
    property0: HaxeEnumProperty(
        'property0',
        items = [('Add', 'Add', 'Add'),
                 ('Subtract', 'Subtract', 'Subtract'),
                 ('DotProduct', 'Dot Product', 'Dot Product'),
                 ('Multiply', 'Multiply', 'Multiply'),
                 ('MultiplyFloats', 'Multiply (Floats)', 'Multiply (Floats)'),
                 ('Module', 'Module', 'Module'),
                 ('Normalize', 'Normalize', 'Normalize'), #],
                 # NOTE: the unused parts need to exist to be read from an old version from the node.
                 # this is so dumb…
                 ('Lerp', 'DO NOT USE',''),
                 ('Slerp', 'DO NOT USE',''),
                 ('FromTo', 'DO NOT USE',''),
                 ('FromMat', 'DO NOT USE',''),
                 ('FromRotationMat', 'DO NOT USE',''),
                 ('ToAxisAngle', 'DO NOT USE',''),
                 ('FromAxisAngle', 'DO NOT USE',''),
                 ('FromEuler', 'DO NOT USE',''),
                 ('GetEuler', 'DO NOT USE','')],
        name='', default='Add')  #, set=set_enum, get=get_enum)
    property0_proxy: EnumProperty(
        items = [('Add', 'Add', 'Add'),
                 ('Subtract', 'Subtract', 'Subtract'),
                 ('DotProduct', 'Dot Product', 'Dot Product'),
                 ('Multiply', 'Multiply', 'Multiply'),
                 ('MultiplyFloats', 'Multiply (Floats)', 'Multiply (Floats)'),
                 ('Module', 'Module', 'Module'),
                 ('Normalize', 'Normalize', 'Normalize')],
        name='', default='Add', set=set_enum, get=get_enum)


    def __init__(self, *args, **kwargs):
        super(QuaternionMathNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Quaternion 0 XYZ', default_value=[0.0, 0.0, 0.0])
        self.add_input('ArmFloatSocket', 'Quaternion 0 W', default_value=1)
        self.add_input('ArmVectorSocket', 'Quaternion 1 XYZ', default_value=[0.0, 0.0, 0.0])
        self.add_input('ArmFloatSocket', 'Quaternion 1 W', default_value=1)
        self.add_output('ArmVectorSocket', 'Result XYZ', default_value=[0.0, 0.0, 0.0])
        self.add_output('ArmFloatSocket', 'Result W', default_value=1)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0_proxy') # Operation
        # Buttons
        if (self.get_count_in(self.property0) == 0):
            row = layout.row(align=True)
            column = row.column(align=True)
            op = column.operator('arm.node_add_input', text='Add Value', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            if (self.property0 == 'Add') or (self.property0 == 'Subtract') or (self.property0 == 'Multiply') or (self.property0 == 'DotProduct'):
                op.name_format = 'Quaternion {0} XYZ;Quaternion {0} W'
            else:
                op.name_format = 'Value {0}'
            if (self.property0 == "MultiplyFloats"):
                op.socket_type = 'ArmFloatSocket'
            else:
                op.socket_type = 'ArmVectorSocket;ArmFloatSocket'

            column = row.column(align=True)
            op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op.node_index = str(id(self))
            if self.property0 != "MultiplyFloats":
                op.count = 2
                op.min_inputs = 4
            else:
                op.min_inputs = 2
            if len(self.inputs) == 4:
                column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 2):
            raise LookupError()

        if self.arm_version == 1 or self.arm_version == 2:
            ret=[]
            if self.property0 == 'GetEuler':
                newself = node_tree.nodes.new('LNSeparateRotationNode')
                ret.append(newself)
                newself.property0='EulerAngles'
                newself.property2='XZY'
                newself.property1='Rad'

                for link in self.inputs[0].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, newself.inputs[0])
            elif self.property0 == 'FromEuler':
                newself = node_tree.nodes.new('LNRotationNode')
                ret.append(newself)
                preconv = node_tree.nodes.new('LNVectorNode')
                ret.append(preconv)
                newself.property0='EulerAngles'
                newself.property2='XZY'
                newself.property1='Rad'
                node_tree.links.new(preconv.outputs[0], newself.inputs[0])

                preconv.inputs[0].default_value = self.inputs[0].default_value
                for link in self.inputs[0].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, preconv.inputs[0])
                preconv.inputs[1].default_value = self.inputs[1].default_value
                for link in self.inputs[1].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, preconv.inputs[1])
                preconv.inputs[2].default_value = self.inputs[2].default_value
                for link in self.inputs[2].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, preconv.inputs[2])
            elif self.property0 == 'ToAxisAngle':
                newself = node_tree.nodes.new('LNSeparateRotationNode')
                ret.append(newself)
                newself.property0='AxisAngle'
                newself.property1='Rad'

                for link in self.inputs[0].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, newself.inputs[0])
            elif self.property0 == 'FromAxisAngle':
                newself = node_tree.nodes.new('LNRotationNode')
                ret.append(newself)
                newself.property0='AxisAngle'
                newself.property1='Rad'

                newself.inputs[0].default_value = self.inputs[1].default_value
                for link in self.inputs[1].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, newself.inputs[0])
                newself.inputs[1].default_value = self.inputs[2].default_value
                for link in self.inputs[2].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, newself.inputs[1])
            elif self.property0 in ('FromMat','FromRotationMat'):
                newself = node_tree.nodes.new('LNSeparateTransformNode')
                ret.append(newself)
                for link in self.inputs[1].links:  # 0 or 1
                    node_tree.links.new(link.from_socket, newself.inputs[0])

            elif self.property0 in ('Lerp','Slerp','FromTo'):
                newself = node_tree.nodes.new('LNRotationMathNode')
                ret.append(newself)
                newself.property0 = self.property0

                for in1, in2 in zip(self.inputs, newself.inputs):
                    if in2.bl_idname == 'ArmRotationSocket':
                        in2.default_value_raw = Rotation.convert_to_quaternion(
                            in1.default_value,0,
                            'EulerAngles','Rad','XZY'
                        )
                    elif in1.bl_idname in ('ArmFloatSocket', 'ArmVectorSocket'):
                        in2.default_value = in1.default_value
                    for link in in1.links:
                        node_tree.links.new(link.from_socket, in2)

            else:
                newself = node_tree.nodes.new('LNQuaternionMathNode')
                ret.append(newself)
                newself.property0 = self.property0

                # convert the inputs… this is going to be hard lmao.
                i_in_1 = 0
                i_in_2 = 0
                while i_in_1 < len(self.inputs):
                    in1 = self.inputs[i_in_1]
                    if in1.bl_idname == 'ArmVectorSocket':
                        # quaternion input: now two sockets, not one.
                        convnode = node_tree.nodes.new('LNSeparateRotationNode')
                        convnode.property0 = 'Quaternion'
                        ret.append(convnode)
                        if i_in_2 >= len(newself.inputs):
                            newself.ensure_input_socket(i_in_2, 'ArmVectorSocket', 'Quaternion %d XYZ'%(i_in_1))
                            newself.ensure_input_socket(i_in_2+1, 'ArmFloatSocket', 'Quaternion %d W'%(i_in_1), 1.0)
                        node_tree.links.new(convnode.outputs[0], newself.inputs[i_in_2])
                        node_tree.links.new(convnode.outputs[1], newself.inputs[i_in_2+1])
                        for link in in1.links:
                            node_tree.links.new(link.from_socket, convnode.inputs[0])
                        i_in_2 +=2
                        i_in_1 +=1
                    elif in1.bl_idname == 'ArmFloatSocket':
                        for link in in1.links:
                            node_tree.links.new(link.from_socket, newself.inputs[i_in_2])
                        i_in_1 +=1
                        i_in_2 +=1
                    else:
                        raise ValueError('get_replacement_node() for is not LNQuaternionMathNode V1->V2 is not prepared to deal with an input socket of type %s. This is a bug to report to the developers' %in1.bl_idname)
            # #### now that the input has been dealt with, let's deal with the output.
            if self.property0 in ('FromEuler','FromMat','FromRotationMat','FromAxisAngle','Lerp','Slerp','FromTo'):
                # the new self returns a rotation
                for link in self.outputs[0].links:
                    out_sock_i = int( self.property0.endswith('Mat') )
                    node_tree.links.new(newself.outputs[out_sock_i], link.to_socket)
            elif self.property0 in ('DotProduct','Module'):
                # new self returns a float
                for link in self.outputs[1 + 4*int(self.property1)].links:
                    node_tree.links.new(newself.outputs[1], link.to_socket)
            elif self.property0 in ('GetEuler', 'ToAxisAngle'):
                # new self returns misc.
                for link in self.outputs[0].links:
                    node_tree.links.new(newself.outputs[0], link.to_socket)
                if self.property0 == 'ToAxisAngle':
                    for link in self.outputs[1 + 4*int(self.property1)].links:
                        node_tree.links.new(newself.outputs[1], link.to_socket)
                if self.property1:
                    xlinks = self.outputs[1].links
                    ylinks = self.outputs[2].links
                    zlinks = self.outputs[3].links
                    if len(xlinks)>0 or len(ylinks)>0 or len(zlinks)>0:
                        conv = node_tree.nodes.new('LNSeparateVectorNode')
                        ret.append(conv)
                        node_tree.links.new(newself.outputs[0], conv.inputs[0])
                        for link in xlinks:
                            node_tree.links.new(conv.outputs[0], link.to_socket)
                        for link in ylinks:
                            node_tree.links.new(conv.outputs[1], link.to_socket)
                        for link in zlinks:
                            node_tree.links.new(conv.outputs[2], link.to_socket)
            else:
                # new self returns a proper quaternion XYZ/W
                outlinks = self.outputs[0].links
                if len(outlinks)>0:
                    conv = node_tree.nodes.new('LNRotationNode')
                    conv.property0='Quaternion'
                    ret.append(conv)
                    node_tree.links.new(newself.outputs[0], conv.inputs[0])
                    node_tree.links.new(newself.outputs[1], conv.inputs[1])
                    for link in outlinks:
                        node_tree.links.new(conv.outputs[0], link.to_socket)
                if self.property1:
                    for link in self.outputs[4].links:  # for W
                        node_tree.links.new(newself.outputs[1], link.to_socket)
                    xlinks = self.outputs[1].links
                    ylinks = self.outputs[2].links
                    zlinks = self.outputs[3].links
                    if len(xlinks)>0 or len(ylinks)>0 or len(zlinks)>0:
                        conv = node_tree.nodes.new('LNSeparateVectorNode')
                        ret.append(conv)
                        node_tree.links.new(newself.outputs[0], conv.inputs[0])
                        for link in xlinks:
                            node_tree.links.new(conv.outputs[0], link.to_socket)
                        for link in ylinks:
                            node_tree.links.new(conv.outputs[1], link.to_socket)
                        for link in zlinks:
                            node_tree.links.new(conv.outputs[2], link.to_socket)
            for node in ret: # update the labels on the node's displays
                if node.bl_idname == 'LNSeparateRotationNode':
                    node.on_property_update(None)
                elif node.bl_idname == 'LNRotationNode':
                    node.on_property_update(None)
                elif node.bl_idname == 'LNRotationMathNode':
                    node.on_update_operation(None)
                elif node.bl_idname == 'LNQuaternionMathNode':
                    node.set_enum(node.get_enum())
            return ret

    # note: keep property1, so that it is actually readable for node conversion.
    property1: BoolProperty(name='DEPRECATED', default=False)