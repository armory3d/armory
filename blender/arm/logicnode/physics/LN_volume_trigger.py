from arm.logicnode.arm_nodes import *

class VolumeTriggerNode(ArmLogicTreeNode):
    """Returns `true` if the given rigid body enters, overlaps or leaves the
    given volume trigger.

    @input Object: this object is taken as the entering object
    @input Volume: this object is used as the volume"""
    bl_idname = 'LNVolumeTriggerNode'
    bl_label = 'Volume Trigger'
    arm_version = 1
    property0: EnumProperty(
        items = [('Enter', 'Enter', 'Enter'),
                 ('Leave', 'Leave', 'Leave'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Enter')

    def init(self, context):
        super(VolumeTriggerNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmNodeSocketObject', 'Trigger')
        self.add_output('NodeSocketBool', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(VolumeTriggerNode, category=PKG_AS_CATEGORY, section='misc')
