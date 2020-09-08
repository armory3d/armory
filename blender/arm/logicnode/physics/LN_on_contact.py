from arm.logicnode.arm_nodes import *

class OnContactNode(ArmLogicTreeNode):
    """On contact node"""
    bl_idname = 'LNOnContactNode'
    bl_label = 'On Contact'
    property0: EnumProperty(
        items = [('Begin', 'Begin', 'Begin'),
                 ('End', 'End', 'End'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Begin')

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object 1')
        self.add_input('ArmNodeSocketObject', 'Object 2')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnContactNode, category=MODULE_AS_CATEGORY, section='contact')
