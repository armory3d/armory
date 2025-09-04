from arm.logicnode.arm_nodes import *


class NetworkSendMessageNode(ArmLogicTreeNode):
    """Send messages directly to a host as a client or to all of the
    network clients connected to a host send messages directly"""
    bl_idname = 'LNNetworkSendMessageNode'
    bl_label = 'Send Message'
    arm_version = 1
    ind = 4

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
                    self.add_input('ArmNodeSocketAction', 'In')
                    self.add_input('ArmDynamicSocket', 'Connection')
                    self.add_input('ArmStringSocket', 'API')
                    self.add_input('ArmDynamicSocket', 'Data')

            # Arguements for type Host
            if (self.get_count_in(select_current) == 1):
                    self.add_input('ArmNodeSocketAction', 'In')
                    self.add_input('ArmDynamicSocket', 'Connection')
                    self.add_input('ArmStringSocket', 'API')
                    self.add_input('ArmDynamicSocket', 'Data')
                    self.add_input('ArmStringSocket', 'ID')
                    self.add_input('ArmBoolSocket', 'Send All')


            # Arguements for type Secure Host
            if (self.get_count_in(select_current) == 2):
                    self.add_input('ArmNodeSocketAction', 'In')
                    self.add_input('ArmDynamicSocket', 'Connection')
                    self.add_input('ArmStringSocket', 'API')
                    self.add_input('ArmDynamicSocket', 'Data')
                    self.add_input('ArmStringSocket', 'ID')
                    self.add_input('ArmBoolSocket', 'Send All')


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
        items = [('string', 'String', 'Send a string over the network to one or all of the clients'),
                 ('vector', 'Vector', 'Send a vector over the network to one or all of the clients'),
                 ('float', 'Float', 'Send a float over the network to one or all of the clients'),
                 ('integer', 'Integer', 'Send an integer over the network to one or all of the clients'),
                 ('boolean', 'Boolean', 'Send a boolean over the network to one or all of the clients'),
                 ('transform', 'Transform', 'Send a transform over the network to one or all of the clients'),
                 ('rotation', 'Rotation', 'Send a rotation over the network to one or all of the clients')],
        name='',
        default='string')


    def __init__(self, *args, **kwargs):
        super(NetworkSendMessageNode, self).__init__(*args, **kwargs)


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Connection')
        self.add_input('ArmStringSocket', 'API')
        self.add_input('ArmDynamicSocket', 'Data')

        self.add_output('ArmNodeSocketAction', 'Out')



    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
