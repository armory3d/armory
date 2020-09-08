from arm.logicnode.arm_nodes import *

class RpSuperSampleNode(ArmLogicTreeNode):
    """Configure super sampling node"""
    bl_idname = 'LNRpSuperSampleNode'
    bl_label = 'Rp Super-sampling'
    property0: EnumProperty(
        items = [('1', '1', '1'),
                 ('1.5', '1.5', '1.5'),
                 ('2', '2', '2'),
                 ('4', '4', '4')
                 ],
        name='', default='1')

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(RpSuperSampleNode, category=MODULE_AS_CATEGORY)
