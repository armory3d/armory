from arm.logicnode.arm_nodes import *

class OnVolumeTriggerNode(ArmLogicTreeNode):
    """Runs the output when the object enter, overlap or leave the trigger."""
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
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Volume', default_value='Volume')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnVolumeTriggerNode, category=PKG_AS_CATEGORY)
