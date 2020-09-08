from arm.logicnode.arm_nodes import *


class TranslateOnLocalAxisNode(ArmLogicTreeNode):
    """TranslateOnLocalAxisNode"""
    bl_idname = 'LNTranslateOnLocalAxisNode'
    bl_label = 'Translate On Local Axis'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketFloat', 'Speed')
        self.add_input('NodeSocketInt', 'Forward/Up/Right')
        self.add_input('NodeSocketBool', 'Inverse')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(TranslateOnLocalAxisNode, category=MODULE_AS_CATEGORY, section='location')
