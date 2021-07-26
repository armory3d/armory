from arm.logicnode.arm_nodes import *

class RpConfigNode(ArmLogicTreeNode):
    """Sets the post process quality."""
    bl_idname = 'LNRpConfigNode'
    bl_label = 'Set Post Process Quality'
    arm_version = 1
    property0: HaxeEnumProperty(
        'property0',
        items = [('SSGI', 'SSGI', 'SSGI'),
                 ('SSR', 'SSR', 'SSR'),
                 ('Bloom', 'Bloom', 'Bloom'),
                 ('GI', 'GI', 'GI'),
                 ('Motion Blur', 'Motion Blur', 'Motion Blur')
                 ],
        name='', default='SSGI')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Enable')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
