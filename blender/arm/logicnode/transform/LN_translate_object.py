from arm.logicnode.arm_nodes import *

class TranslateObjectNode(ArmLogicTreeNode):
    """Translate object node"""
    bl_idname = 'LNTranslateObjectNode'
    bl_label = 'Translate Object'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Vector')
        self.add_input('NodeSocketBool', 'On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(TranslateObjectNode, category=PKG_AS_CATEGORY, section='location')
