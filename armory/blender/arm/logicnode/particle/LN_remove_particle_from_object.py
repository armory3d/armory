from arm.logicnode.arm_nodes import *

class RemoveParticleFromObjectNode(ArmLogicTreeNode):
    """Remove Particle From Object."""
    bl_idname = 'LNRemoveParticleFromObjectNode'
    bl_label = 'Remove Particle From Object'
    arm_version = 1

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 2:
                self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Slot':
            self.add_input('ArmIntSocket', 'Slot')
        if self.property0 == 'Name':
            self.add_input('ArmStringSocket', 'Name')

    property0: HaxeEnumProperty(
    'property0',
    items = [('Slot', 'Slot', 'Slot'),
             ('Name', 'Name', 'Name'),
             ('All', 'All', 'All')],
    name='', default='Slot', update=remove_extra_inputs)
    

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmIntSocket', 'Slot')

        self.add_output('ArmNodeSocketAction', 'Out')
        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
