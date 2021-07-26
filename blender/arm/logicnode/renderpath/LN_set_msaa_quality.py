from arm.logicnode.arm_nodes import *

class RpMSAANode(ArmLogicTreeNode):
    """Sets the MSAA quality."""
    bl_idname = 'LNRpMSAANode'
    bl_label = 'Set MSAA Quality'
    arm_version = 1
    property0: HaxeEnumProperty(
        'property0',
        items = [('1', '1', '1'),
                 ('2', '2', '2'),
                 ('4', '4', '4'),
                 ('8', '8', '8'),
                 ('16', '16', '16')
                 ],
        name='', default='1')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
