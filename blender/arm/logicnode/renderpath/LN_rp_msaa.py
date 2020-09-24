from arm.logicnode.arm_nodes import *

class RpMSAANode(ArmLogicTreeNode):
    """Use to set the MSAA quality."""
    bl_idname = 'LNRpMSAANode'
    bl_label = 'Rp MSAA'
    arm_version = 1
    property0: EnumProperty(
        items = [('1', '1', '1'),
                 ('2', '2', '2'),
                 ('4', '4', '4'),
                 ('8', '8', '8'),
                 ('16', '16', '16')
                 ],
        name='', default='1')

    def init(self, context):
        super(RpMSAANode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(RpMSAANode, category=PKG_AS_CATEGORY)
