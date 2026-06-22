from arm.logicnode.arm_nodes import *

class SetParticleDataNode(ArmLogicTreeNode):
    """Sets the parameters of the given particle system."""
    bl_idname = 'LNSetParticleDataNode'
    bl_label = 'Set Particle Data'
    arm_version = 1

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 3:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Particle Size':
            self.add_input('ArmFloatSocket', 'Particle Size')
        if self.property0 == 'Frame End':
            self.add_input('ArmIntSocket', 'Frame End')
        if self.property0 == 'Frame Start':
            self.add_input('ArmIntSocket', 'Frame Start')
        if self.property0 == 'Lifetime': 
            self.add_input('ArmIntSocket', 'Lifetime')
        if self.property0 == 'Lifetime Random':
            self.add_input('ArmFloatSocket', 'Lifetime Random')
        if self.property0 == 'Emit From':
            self.add_input('ArmIntSocket', 'Emit From')
        if self.property0 == 'Auto Start':
            self.add_input('ArmBoolSocket', 'Auto Start')
        if self.property0 == 'Is Unique':
            self.add_input('ArmBoolSocket', 'Is Unique')
        if self.property0 == 'Loop':
            self.add_input('ArmBoolSocket', 'Loop')
        if self.property0 == 'Velocity':
            self.add_input('ArmVectorSocket', 'Velocity')
        if self.property0 == 'Velocity Random':
            self.add_input('ArmFloatSocket', 'Velocity Random')
        if self.property0 == 'Weight Gravity':
            self.add_input('ArmFloatSocket', 'Weight Gravity')
        if self.property0 == 'Speed':
            self.add_input('ArmFloatSocket', 'Speed')

       
    property0: HaxeEnumProperty(
    'property0',
    items = [('Particle Size', 'Particle Size', 'for the system'),
             ('Frame Start', 'Frame Start', 'for the system'),
             ('Frame End', 'Frame End', 'for the system'),
             ('Lifetime', 'Lifetime', 'for the instance'),
             ('Lifetime Random', 'Lifetime Random', 'for the system'),
             ('Emit From', 'Emit From', 'for the system (Vertices:0 Faces:1 Volume: 2)'),
             ('Auto Start', 'Auto Start', 'for the system'),
             ('Is Unique', 'Is Unique', 'for the system'),
             ('Loop', 'Loop', 'for the system'),
             ('Velocity', 'Velocity', 'for the instance'),
             ('Velocity Random', 'Velocity Random', 'for the system'),
             ('Weight Gravity', 'Weight Gravity', 'for the instance'),
             ('Speed', 'Speed', 'for the instance')],
    name='', default='Speed', update=remove_extra_inputs)
    

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmIntSocket', 'Slot')
        self.add_input('ArmFloatSocket', 'Speed', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')
        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')