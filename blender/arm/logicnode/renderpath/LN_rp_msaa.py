from arm.logicnode.arm_nodes import *

class RpMSAANode(ArmLogicTreeNode):
    """Configure multi-sample anti-aliasing node"""
    bl_idname = 'LNRpMSAANode'
    bl_label = 'Rp MSAA'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('1', '1', '1'),
                 ('2', '2', '2'),
                 ('4', '4', '4'),
                 ('8', '8', '8'),
                 ('16', '16', '16')
                 ],
        name='', default='1')

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(RpMSAANode, category=MODULE_AS_CATEGORY)
