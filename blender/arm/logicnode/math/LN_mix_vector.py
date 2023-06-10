from arm.logicnode.arm_nodes import *

class VectorMixNode(ArmLogicTreeNode):
    """Interpolates between the two given vectors."""
    bl_idname = 'LNVectorMixNode'
    bl_label = 'Mix Vector'
    arm_section = 'vector'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('Linear', 'Linear', 'Linear'),
                 ('Sine', 'Sine', 'Sine'),
                 ('Quad', 'Quad', 'Quad'),
                 ('Cubic', 'Cubic', 'Cubic'),
                 ('Quart', 'Quart', 'Quart'),
                 ('Quint', 'Quint', 'Quint'),
                 ('Expo', 'Expo', 'Expo'),
                 ('Circ', 'Circ', 'Circ'),
                 ('Back', 'Back', 'Back'),
                 ('Bounce', 'Bounce', 'Bounce'),
                 ('Elastic', 'Elastic', 'Elastic'),
                 ],
        name='', default='Linear')
    property1: HaxeEnumProperty(
        'property1',
        items = [('In', 'In', 'In'),
                 ('Out', 'Out', 'Out'),
                 ('InOut', 'InOut', 'InOut'),
                 ],
        name='', default='Out')

    property2: HaxeBoolProperty('property2', name='Clamp', default=False)

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Factor', default_value=0.0)
        self.add_input('ArmVectorSocket', 'Vector 1', default_value=[0.0, 0.0, 0.0])
        self.add_input('ArmVectorSocket', 'Vector 2', default_value=[1.0, 1.0, 1.0])

        self.add_output('ArmVectorSocket', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property2')
        layout.prop(self, 'property0')
        if self.property0 != 'Linear':
            layout.prop(self, 'property1')
