from arm.logicnode.arm_nodes import *

class SurfaceNode(ArmLogicTreeNode):
    """Activates the output on the given touch event."""
    bl_idname = 'LNMergedSurfaceNode'
    bl_label = 'Touch'
    arm_section = 'surface'
    arm_version = 1

    property0: EnumProperty(
        items = [('Started', 'Started', 'The screen surface starts to be touched'),
                 ('Down', 'Down', 'The screen surface is touched'),
                 ('Released', 'Released', 'The screen surface stops being touched'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Down')

    def init(self, context):
        super(SurfaceNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
