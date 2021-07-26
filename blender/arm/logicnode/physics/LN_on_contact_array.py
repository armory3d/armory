from arm.logicnode.arm_nodes import *

class OnContactArrayNode(ArmLogicTreeNode):
    """Activates the output when the given rigid body make contact with other given rigid bodies."""
    bl_idname = 'LNOnContactArrayNode'
    bl_label = 'On Contact Array'
    arm_section = 'contact'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('begin', 'Begin', 'The contact between the rigid bodies begins'),
                 ('overlap', 'Overlap', 'The contact between the rigid bodies is happening'),
                 ('end', 'End', 'The contact between the rigid bodies ends')],
        name='', default='begin')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmNodeSocketArray', 'RBs')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
