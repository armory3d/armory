from arm.logicnode.arm_nodes import *

class OnVolumeTriggerNode(ArmLogicTreeNode):
    """Activates the output when the given object enters, overlaps or leaves the bounding box of the given trigger object. (Note: Works even if objects are not Rigid Bodies).

    @input RB: this object is taken as the entering object
    @input Trigger: this object is used as the volume trigger
    """
    bl_idname = 'LNOnVolumeTriggerNode'
    bl_label = 'On Volume Trigger'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('begin', 'Begin', 'The contact between the rigid bodies begins'),
                 ('overlap', 'Overlap', 'The contact between the rigid bodies is happening'),
                 ('end', 'End', 'The contact between the rigid bodies ends')],
        name='', default='begin')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object 1')
        self.add_input('ArmNodeSocketObject', 'Object 2')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
