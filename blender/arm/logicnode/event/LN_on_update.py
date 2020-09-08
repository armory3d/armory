from arm.logicnode.arm_nodes import *

class OnUpdateNode(ArmLogicTreeNode):
    """On update node"""
    bl_idname = 'LNOnUpdateNode'
    bl_label = 'On Update'
    property0: EnumProperty(
        items = [('Update', 'Update', 'Update'),
                 ('Late Update', 'Late Update', 'Late Update'),
                 ('Physics Pre-Update', 'Physics Pre-Update', 'Physics Pre-Update')],
        name='On', default='Update')

    def init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnUpdateNode, category=MODULE_AS_CATEGORY)
