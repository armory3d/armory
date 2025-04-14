from arm.logicnode.arm_nodes import *

class SetNishitaPropertiesNode(ArmLogicTreeNode):
    """Sets the Nishita properties"""
    bl_idname = 'LNSetNishitaPropertiesNode'
    bl_label = 'Set Nishita Properties'
    arm_version = 1
    
    def remove_extra_inputs(self, context):
        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Density':
            self.add_input('ArmFloatSocket', 'Air')
            self.add_input('ArmFloatSocket', 'Dust')
            self.add_input('ArmFloatSocket', 'Ozone')
        if self.property0 == 'Air':
           self.add_input('ArmFloatSocket', 'Air')
        if self.property0 == 'Dust':
            self.add_input('ArmFloatSocket', 'Dust')
        if self.property0 == 'Ozone':
            self.add_input('ArmFloatSocket', 'Ozone')
        if self.property0 == 'Sun Direction':
            self.add_input('ArmVectorSocket', 'Sun Direction')

    property0: HaxeEnumProperty(
    'property0',
    items = [('Density', 'Density', 'Air, Dust, Ozone'),
             ('Air', 'Air', 'Air'),
             ('Dust', 'Dust', 'Dust'),
             ('Ozone', 'Ozone', 'Ozone'),
             ('Sun Direction', 'Sun Direction', 'Sun Direction')],
    name='', default='Density', update=remove_extra_inputs)

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Air')
        self.add_input('ArmFloatSocket', 'Dust')
        self.add_input('ArmFloatSocket', 'Ozone')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')