from arm.logicnode.arm_nodes import *

class SurfaceNode(ArmLogicTreeNode):
    """Activates the output on the given touch event."""
    bl_idname = 'LNMergedSurfaceNode'
    bl_label = 'Touch'
    arm_section = 'surface'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('started', 'Started', 'The screen surface starts to be touched'),
                 ('down', 'Down', 'The screen surface is touched'),
                 ('released', 'Released', 'The screen surface stops being touched'),
                 ('moved', 'Moved', 'Moved')],
        name='', default='down')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property0}'
