from arm.logicnode.arm_nodes import *

class MouseNode(ArmLogicTreeNode):
    """Activates the output when the given mouse action is done."""
    bl_idname = 'LNMergedMouseNode'
    bl_label = 'Mouse'
    arm_section = 'mouse'
    arm_version = 1

    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Down')
    property1: EnumProperty(
        items = [('left', 'left', 'left'),
                 ('right', 'right', 'right'),
                 ('middle', 'middle', 'middle')],
        name='', default='left')

    def init(self, context):
        super(MouseNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
