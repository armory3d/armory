from arm.logicnode.arm_nodes import *

class GetDateTimeNode(ArmLogicTreeNode):
    """Returns the values of the current date and time."""
    bl_idname = 'LNGetDateTimeNode'
    bl_label = 'Get Date and Time'
    arm_section = 'Native'
    arm_version = 1

    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(type_name):
        return {
            'now': 0,
            'timestamp': 1,
            'timeZoneOffSet': 2,
            'weekday': 3,
            'day': 4,
            'month': 5,
            'year': 6,
            'hours': 7,
            'minutes': 8,
            'seconds': 9,
            'all': 10,
            'formatted': 11,
        }.get(type_name, 10)

    def get_enum(self):
        return self.get('property0', 10)

    def set_enum(self, value):
        # Checking the selection of each type
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0

        #Check if type changed
        if select_prev != select_current:

            for i in self.inputs:
                self.inputs.remove(i)
            for i in self.outputs:
                self.outputs.remove(i)

            if (self.get_count_in(select_current) == 0):
                    self.add_output('ArmStringSocket', 'Date')
            elif (self.get_count_in(select_current) == 10):
                    self.add_input('ArmNodeSocketAction', 'In')
                    self.add_output('ArmNodeSocketAction', 'Out')
                    self.add_output('ArmIntSocket', 'Timestamp')
                    self.add_output('ArmIntSocket', 'Timezone Offset')
                    self.add_output('ArmIntSocket', 'Weekday')
                    self.add_output('ArmIntSocket', 'Day')
                    self.add_output('ArmIntSocket', 'Month')
                    self.add_output('ArmIntSocket', 'Year')
                    self.add_output('ArmIntSocket', 'Hours')
                    self.add_output('ArmIntSocket', 'Minutes')
                    self.add_output('ArmIntSocket', 'Seconds')
            elif (self.get_count_in(select_current) == 11):
                    self.add_input('ArmStringSocket', 'Format', default_value="%Y/%m/%d - %H:%M:%S")
                    self.add_output('ArmStringSocket', 'Date')
            else:
                self.add_output('ArmIntSocket', 'Value')

        self['property0'] = value


    property0: HaxeEnumProperty(
        'property0',
        items = [('now', 'Now', 'Returns a Date representing the current local time.'),
                ('timestamp', 'Timestamp', 'Returns the timestamp (in milliseconds) of this date'),
                ('timeZoneOffSet', 'Timezone Offset', 'Returns the time zone difference of this Date in the current locale to UTC, in minutes'),
                ('weekday', 'Weekday', 'Returns the day of the week of this Date (0-6 range, where 0 is Sunday) in the local timezone.'),
                ('day', 'Day', 'Returns the day of this Date (1-31 range) in the local timezone.'),
                ('month', 'Month', 'Returns the month of this Date (0-11 range) in the local timezone. Note that the month number is zero-based.'),
                ('year', 'Year', 'Returns the full year of this Date (4 digits) in the local timezone.'),
                ('hours', 'Hours', 'Returns the hours of this Date (0-23 range) in the local timezone.'),
                ('minutes', 'Minutes', 'Returns the minutes of this Date (0-59 range) in the local timezone.'),
                ('seconds', 'Seconds', 'Returns the seconds of this Date (0-59 range) in the local timezone.'),
                ('all', 'All', 'Get all of the individual separated date and time properties'),
                ('formatted', 'Formatted', 'Format the current system date and time')],
        name='',
        default='all',
        set=set_enum,
        get=get_enum)




    def __init__(self, *args, **kwargs):
        super(GetDateTimeNode, self).__init__(*args, **kwargs)


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'Timestamp')
        self.add_output('ArmIntSocket', 'Timezone Offset')
        self.add_output('ArmIntSocket', 'Weekday')
        self.add_output('ArmIntSocket', 'Day')
        self.add_output('ArmIntSocket', 'Month')
        self.add_output('ArmIntSocket', 'Year')
        self.add_output('ArmIntSocket', 'Hours')
        self.add_output('ArmIntSocket', 'Minutes')
        self.add_output('ArmIntSocket', 'Seconds')



    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

