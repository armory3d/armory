from arm.logicnode.arm_nodes import *


class TranslateOnLocalAxisNode(ArmLogicTreeNode):
    """Use to translate an object in the local axis."""
    bl_idname = 'LNTranslateOnLocalAxisNode'
    bl_label = 'Translate On Local Axis'
    arm_version = 1

    def init(self, context):
        super(TranslateOnLocalAxisNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketFloat', 'Speed')
        self.add_input('NodeSocketInt', 'Forward/Up/Right')
        self.add_input('NodeSocketBool', 'Inverse')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(TranslateOnLocalAxisNode, category=PKG_AS_CATEGORY, section='location')
