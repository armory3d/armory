from arm.logicnode.arm_nodes import *

class SetHosekWilkiePropertiesNode(ArmLogicTreeNode):
    """Sets the HosekWilkie properties."""
    bl_idname = 'LNSetHosekWilkiePropertiesNode'
    bl_label = 'Set HosekWilkie Properties'
    arm_version = 1
    
    def remove_extra_inputs(self, context):
        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Turbidity/Ground Albedo':
            self.add_input('ArmFloatSocket', 'Turbidity')
            self.add_input('ArmFloatSocket', 'Ground Albedo')
        if self.property0 == 'Turbidity':
            self.add_input('ArmFloatSocket', 'Turbidity')
        if self.property0 == 'Ground Albedo':
            self.add_input('ArmFloatSocket', 'Ground Albedo')
        if self.property0 == 'Sun Direction':
            self.add_input('ArmVectorSocket', 'Sun Direction')

    property0: HaxeEnumProperty(
    'property0',
    items = [('Turbidity/Ground Albedo', 'Turbidity/Ground Albedo', 'Turbidity, Ground Albedo'), 
             ('Turbidity', 'Turbidity', 'Turbidity'),
             ('Ground Albedo', 'Ground Albedo', 'Ground Albedo'),
             ('Sun Direction', 'Sun Direction', 'Sun Direction')],
    name='', default='Turbidity/Ground Albedo', update=remove_extra_inputs)

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Turbidity')
        self.add_input('ArmFloatSocket', 'Ground_Albedo')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')