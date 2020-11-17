from arm.logicnode.arm_nodes import *

class OnVolumeTriggerNode(ArmLogicTreeNode):
    """Activates the output when the given rigid body enter, overlap or leave the given trigger.

    @input RB: this object is taken as the entering object
    @input Trigger: this object is used as the volume trigger
    """
    bl_idname = 'LNOnVolumeTriggerNode'
    bl_label = 'On Volume Trigger'
    arm_version = 1

    property0: EnumProperty(
        items = [('Begin', 'Begin', 'The contact between the rigid bodies starts'),
                 ('Overlap', 'Overlap', 'The contact between the rigid bodies is happening'),
                 ('End', 'End', 'The contact between the rigid bodies ends')],
        name='', default='Begin')

    def init(self, context):
        super(OnVolumeTriggerNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmNodeSocketObject', 'Trigger')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
