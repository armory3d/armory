from arm.logicnode.arm_nodes import *

class MouseNode(ArmLogicTreeNode):
    """Activates the output on the given mouse event."""
    bl_idname = 'LNMergedMouseNode'
    bl_label = 'Mouse'
    arm_section = 'mouse'
    arm_version = 1

    property0: EnumProperty(
        items = [('started', 'Started', 'The mouse button startes to be pressed'),
                 ('down', 'Down', 'The mouse button is pressed'),
                 ('released', 'Released', 'The mouse button stops being pressed'),
                 ('moved', 'Moved', 'Moved')],
        name='', default='down')
    property1: EnumProperty(
        items = [('left', 'Left', 'Left'),
                 ('middle', 'Middle', 'Middle'),
                 ('right', 'Right', 'Right')],
        name='', default='left')

    def init(self, context):
        super(MouseNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
