from arm.logicnode.arm_nodes import *

class AddParticleToObjectNode(ArmLogicTreeNode):
    """Sets the speed of the given particle source."""
    bl_idname = 'LNAddParticleToObjectNode'
    bl_label = 'Add Particle To Object'
    arm_version = 1

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Scene':
            self.add_input('ArmStringSocket', 'Scene From Name')
            self.add_input('ArmStringSocket', 'Object From Name')
        else:
            self.add_input('ArmNodeSocketObject', 'Object From')
        self.add_input('ArmIntSocket', 'Slot')
        self.add_input('ArmNodeSocketObject', 'Object To')
        self.add_input('ArmBoolSocket', 'Render Emitter', default_value = True)


    property0: HaxeEnumProperty(
    'property0',
    items = [('Scene Active', 'Scene Active', 'Scene Active'),
             ('Scene', 'Scene', 'Scene')],
    name='', default='Scene Active', update=remove_extra_inputs)


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object From')
        self.add_input('ArmIntSocket', 'Slot')
        self.add_input('ArmNodeSocketObject', 'Object To')
        self.add_input('ArmBoolSocket', 'Render Emitter', default_value = True)

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
       

