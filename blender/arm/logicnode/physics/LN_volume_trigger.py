from arm.logicnode.arm_nodes import *

class VolumeTriggerNode(ArmLogicTreeNode):
    """Returns `true` if the given rigid body enters, overlaps or leaves the
    given volume trigger.

    @input RB: this object is taken as the entering object
    @input Trigger: this object is used as the volume trigger
    """
    bl_idname = 'LNVolumeTriggerNode'
    bl_label = 'Volume Trigger'
    arm_section = 'misc'
    arm_version = 1

    property0: EnumProperty(
        items = [('Begin', 'Begin', 'The contact between the rigid bodies starts'),
                 ('Overlap', 'Overlap', 'The contact between the rigid bodies is happening'),
                 ('End', 'End', 'The contact between the rigid bodies ends')],
        name='', default='Begin')

    def init(self, context):
        super(VolumeTriggerNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmNodeSocketObject', 'Trigger')

        self.add_output('NodeSocketBool', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
