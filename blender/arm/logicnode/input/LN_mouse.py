from arm.logicnode.arm_nodes import *

class MouseNode(ArmLogicTreeNode):
    """Activates the output on the given mouse event."""
    bl_idname = 'LNMergedMouseNode'
    bl_label = 'Mouse'
    arm_section = 'mouse'
    arm_version = 1

    property0: EnumProperty(
        items = [('Started', 'Started', 'The mouse button startes to be pressed'),
                 ('Down', 'Down', 'The mouse button is pressed'),
                 ('Released', 'Released', 'The mouse button stops being pressed'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Down')
    property1: EnumProperty(
        items = [('Left', 'Left', 'Left'),
                 ('Middle', 'Middle', 'Middle'),
                 ('Right', 'Right', 'Right')],
        name='', default='Left')

    def init(self, context):
        super(MouseNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
