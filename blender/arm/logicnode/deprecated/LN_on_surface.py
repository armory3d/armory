from arm.logicnode.arm_nodes import *


@deprecated('Surface')
class OnSurfaceNode(ArmLogicTreeNode):
    """Deprecated. Is recommended to use the 'Surface' node instead."""
    bl_idname = 'LNOnSurfaceNode'
    bl_label = 'On Surface'
    bl_description = "Please use the \"Surface\" node instead"
    arm_category = 'Input'
    arm_section = 'surface'
    arm_version = 2

    property0: HaxeEnumProperty(
        'property0',
        items = [('Touched', 'Touched', 'Touched'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Touched')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
