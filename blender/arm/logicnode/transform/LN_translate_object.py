from arm.logicnode.arm_nodes import *

class TranslateObjectNode(ArmLogicTreeNode):
    """Translates (moves) the given object using the given vector in world coordinates."""
    bl_idname = 'LNTranslateObjectNode'
    bl_label = 'Translate Object'
    arm_section = 'location'
    arm_version = 1

    def init(self, context):
        super(TranslateObjectNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Vector')
        self.add_input('NodeSocketBool', 'On Local Axis')

        self.add_output('ArmNodeSocketAction', 'Out')
