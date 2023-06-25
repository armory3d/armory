from arm.logicnode.arm_nodes import *


class NetworkHttpRequestNode(ArmLogicTreeNode):
    """Network Http Request"""
    bl_idname = 'LNNetworkHttpRequestNode'
    bl_label = 'Http Request'
    arm_version = 1


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

        if select_prev != select_current:

            for i in self.inputs:
                self.inputs.remove(i)
            for i in self.outputs:
                self.outputs.remove(i)

        if (self.get_count_in(select_current) == 0):
            self.add_input('ArmNodeSocketAction', 'In')
            self.add_input('ArmStringSocket', 'Url')
            self.add_input('ArmDynamicSocket', 'Headers')
            self.add_input('ArmDynamicSocket', 'Parameters')
            self.add_output('ArmNodeSocketAction', 'Out')
            self.add_output('ArmIntSocket', 'Status')
            self.add_output('ArmDynamicSocket', 'Response')
            self['property0'] = value
        else:
            self.add_input('ArmNodeSocketAction', 'In')
            self.add_input('ArmStringSocket', 'Url')
            self.add_input('ArmDynamicSocket', 'Data')
            self.add_input('ArmBoolSocket', 'Bytes')
            self.add_input('ArmDynamicSocket', 'Headers')
            self.add_input('ArmDynamicSocket', 'Parameters')
            self.add_output('ArmNodeSocketAction', 'Out')
            self.add_output('ArmIntSocket', 'Status')
            self.add_output('ArmDynamicSocket', 'Response')
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

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'Status')
        self.add_output('ArmDynamicSocket', 'Response')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
