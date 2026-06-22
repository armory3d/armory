from arm.logicnode.arm_nodes import *

class RpShadowQualityNode(ArmLogicTreeNode):
    """Sets the shadows quality."""
    bl_idname = 'LNRpShadowQualityNode'
    bl_label = 'Set Shadows Quality'
    arm_version = 1
    property0: HaxeEnumProperty(
        'property0',
        items = [('High', 'High', 'High'),
                 ('Medium', 'Medium', 'Medium'),
                 ('Low', 'Low', 'Low')
                 ],
        name='', default='Medium')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
