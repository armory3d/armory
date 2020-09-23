from arm.logicnode.arm_nodes import *

class OnSurfaceNode(ArmLogicTreeNode):
    """Deprecated. Is recommended to use Surface node instead."""
    bl_idname = 'LNOnSurfaceNode'
    bl_label = 'On Surface'
    arm_version = 1
    property0: EnumProperty(
        items = [('Touched', 'Touched', 'Touched'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Touched')

    def init(self, context):
        super(OnSurfaceNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnSurfaceNode, category=PKG_AS_CATEGORY, section='surface')
