from arm.logicnode.arm_nodes import *

class OnVolumeTriggerNode(ArmLogicTreeNode):
    """Activates the output when the given rigid body enter, overlap or leave the given trigger."""
    bl_idname = 'LNOnVolumeTriggerNode'
    bl_label = 'On Volume Trigger'
    arm_version = 1
    property0: EnumProperty(
        items = [('Enter', 'Enter', 'Enter'),
                 ('Leave', 'Leave', 'Leave'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Enter')

    def init(self, context):
        super(OnVolumeTriggerNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmNodeSocketObject', 'Trigger')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
