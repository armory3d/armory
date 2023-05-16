from arm.logicnode.arm_nodes import *

class RpSuperSampleNode(ArmLogicTreeNode):
    """Sets the supersampling quality."""
    bl_idname = 'LNRpSuperSampleNode'
    bl_label = 'Set SSAA Quality'
    arm_version = 1
    property0: HaxeEnumProperty(
        'property0',
        items = [('1', '1', '1'),
                 ('1.5', '1.5', '1.5'),
                 ('2', '2', '2'),
                 ('4', '4', '4')
                 ],
        name='', default='1')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
