from arm.logicnode.arm_nodes import *

class OnContactArrayNode(ArmLogicTreeNode):
    """Activates the output when the given rigid body make contact with other given rigid bodies."""
    bl_idname = 'LNOnContactArrayNode'
    bl_label = 'On Contact Array'
    arm_section = 'contact'
    arm_version = 1

    property0: EnumProperty(
        items = [('Begin', 'Begin', 'Begin'),
                 ('End', 'End', 'End'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Begin')

    def init(self, context):
        super(OnContactArrayNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmNodeSocketArray', 'RBs')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
