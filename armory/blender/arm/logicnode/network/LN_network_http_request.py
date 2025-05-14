from arm.logicnode.arm_nodes import *


class NetworkHttpRequestNode(ArmLogicTreeNode):
    """Network HTTP Request.

    @option Get/ Post: Use HTTP GET or POST methods.

    @input In: Action input.

    @input Url: Url as string.

    @input Headers: Headers as a Haxe map.

    @input Parameters: Parameters for the request as Haxe map.

    @seeNode Create Map

    @input Print Error: Print Error in console.

    @input Data: Data to send. Any type.

    @input Bytes: Is the data sent as bytes or as a string.

    @output Out: Multi-functional output. Type of output given by `Callback Type`.

    @output Callback Type: Type of output.
    0 = Node Executed
    1 = Status Callback
    2 = Bytes Data Response Callback
    3 = String Data Response Callback
    4 = Error String Callback

    @utput Status: Status value

    @utput Response: Response value

    @output Error: Error
    """

    bl_idname = 'LNNetworkHttpRequestNode'
    bl_label = 'Http Request'
    arm_version = 2

    default_inputs_count = 5


    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(type_name):
        return {
            'get': 0,
            'post': 1
        }.get(type_name, 0)

    def get_enum(self):
        return self.get('property0', 0)

    def set_enum(self, value):
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0

        if select_prev == select_current:
            return

        if (self.get_count_in(select_current) == 0):
            idx = 0
            for inp in self.inputs:
                if idx >= self.default_inputs_count:
                    self.inputs.remove(inp)
                idx += 1
            self['property0'] = value
        else:
            self.add_input('ArmDynamicSocket', 'Data')
            self.add_input('ArmBoolSocket', 'Bytes')
            self['property0'] = value
 

    property0: HaxeEnumProperty(
        'property0',
        items = [('get', 'Get', 'Http get request'),
                ('post', 'Post', 'Http post request')],
        name='', default='get',
        set=set_enum, 
        get=get_enum)


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Url')
        self.add_input('ArmDynamicSocket', 'Headers')
        self.add_input('ArmDynamicSocket', 'Parameters')
        self.add_input('ArmBoolSocket', 'Print Error')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'Callback Type')
        self.add_output('ArmIntSocket', 'Status')
        self.add_output('ArmDynamicSocket', 'Response')
        self.add_output('ArmStringSocket', 'Error')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNNetworkHttpRequestNode', self.arm_version, 'LNNetworkHttpRequestNode', 2,
            in_socket_mapping = {0:0, 1:1}, out_socket_mapping={0:0}
        )