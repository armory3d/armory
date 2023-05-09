from arm.logicnode.arm_nodes import *


@deprecated('Virtual Button')
class OnVirtualButtonNode(ArmLogicTreeNode):
    """Deprecated. Is recommended to use 'Virtual Button' node instead."""
    bl_idname = 'LNOnVirtualButtonNode'
    bl_label = 'On Virtual Button'
    bl_description = "Please use the \"Virtual Button\" node instead"
    arm_category = 'Input'
    arm_section = 'virtual'
    arm_version = 2

    property0: HaxeEnumProperty(
        'property0',
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Started')
    property1: HaxeStringProperty('property1', name='', default='button')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
