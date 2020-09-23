from arm.logicnode.arm_nodes import *

class OnContactArrayNode(ArmLogicTreeNode):
    """Runs the output when the rigid body make contact with other rigid bodies."""
    bl_idname = 'LNOnContactArrayNode'
    bl_label = 'On Contact Array'
    arm_version = 1
    property0: EnumProperty(
        items = [('Begin', 'Begin', 'Begin'),
                 ('End', 'End', 'End'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Begin')

    def init(self, context):
        super(OnContactArrayNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('ArmNodeSocketArray', 'Rigid Bodies')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnContactArrayNode, category=PKG_AS_CATEGORY, section='contact')
