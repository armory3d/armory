from arm.logicnode.arm_nodes import *

class OnVirtualButtonNode(ArmLogicTreeNode):
    """Deprecated. Is recommended to use 'Virtual Button' node instead."""
    bl_idname = 'LNOnVirtualButtonNode'
    bl_label = 'On Virtual Button'
    bl_description = "Please use the \"Virtual Button\" node instead"
    bl_icon = 'ERROR'
    arm_version = 2
    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Started')
    property1: StringProperty(name='', default='button')

    def init(self, context):
        super(OnVirtualButtonNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(OnVirtualButtonNode, category=PKG_AS_CATEGORY, section='virtual', is_obsolete=True)
