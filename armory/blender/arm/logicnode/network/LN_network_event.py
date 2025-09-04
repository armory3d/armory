from arm.logicnode.arm_nodes import *


class NetworkEventNode(ArmLogicTreeNode):
    """Triggers an event from the network getting both message data and sender ID"""
    bl_idname = 'LNNetworkEventNode'
    bl_label = 'Network Event'
    arm_version = 1

    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(type_name):
        return {
            'client': 0,
            'host': 1,
            'securehost': 2
        }.get(type_name, 0)

    def get_enum(self):
        return self.get('property0', 0)

    def set_enum(self, value):
        # Checking the selection of each type
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0

        #Check if type changed
        if select_prev != select_current:

            for i in self.inputs:
                self.inputs.remove(i)

            # Arguements for type Client
            if (self.get_count_in(select_current) == 0):
                    self.add_input('ArmStringSocket', 'Url', default_value="ws://127.0.0.1:8001")


            # Arguements for type Host
            if (self.get_count_in(select_current) == 1):
                    self.add_input('ArmStringSocket', 'Domain', default_value="127.0.0.1")
                    self.add_input('ArmIntSocket', 'Port', default_value=8001)


            # Arguements for type Secure Host
            if (self.get_count_in(select_current) == 2):
                    self.add_input('ArmStringSocket', 'Domain', default_value="127.0.0.1")
                    self.add_input('ArmIntSocket', 'Port', default_value=8001)


        self['property0'] = value


    property0: HaxeEnumProperty(
        'property0',
        items = [('client', 'Client', 'Network client Event listener'),
                ('host', 'Host', 'Network host Event listener'),
                ('securehost', 'Secure Host', 'Network secure host Event listener')],
        name='',
        default='client',
        set=set_enum,
        get=get_enum)


    property1: HaxeEnumProperty(
        'property1',
        items = [('onopen', 'OnOpen', 'Listens to onOpen event'),
                 ('onmessage', 'OnMessage', 'Listens to onMessage event'),
                 ('onerror', 'OnError', 'Listens to onError event'),
                 ('onclose', 'OnClose', 'Listens to onClose event')],
        name='',
        default='onopen')


    def __init__(self, *args, **kwargs):
        super(NetworkEventNode, self).__init__(*args, **kwargs)


    def arm_init(self, context):
        #self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Url', default_value="ws://127.0.0.1:8001")

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'ID')
        self.add_output('ArmDynamicSocket', 'Data')


    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
