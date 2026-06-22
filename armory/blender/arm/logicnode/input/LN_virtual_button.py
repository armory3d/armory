from arm.logicnode.arm_nodes import *

class VirtualButtonNode(ArmLogicTreeNode):
    """Activates the output on the given virtual button event."""
    bl_idname = 'LNMergedVirtualButtonNode'
    bl_label = 'Virtual Button'
    arm_section = 'virtual'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('started', 'Started', 'The virtual button starts to be pressed'),
                 ('down', 'Down', 'The virtual button is pressed'),
                 ('released', 'Released', 'The virtual button stops being pressed')],
        name='', default='down')
    property1: HaxeStringProperty('property1', name='', default='button')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property1}'
