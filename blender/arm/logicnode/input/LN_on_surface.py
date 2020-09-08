from arm.logicnode.arm_nodes import *

class OnSurfaceNode(ArmLogicTreeNode):
    """On surface node"""
    bl_idname = 'LNOnSurfaceNode'
    bl_label = 'On Surface'
    property0: EnumProperty(
        items = [('Touched', 'Touched', 'Touched'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Touched')

    def init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnSurfaceNode, category=MODULE_AS_CATEGORY, section='surface')
