from arm.logicnode.arm_nodes import *


class TranslateOnLocalAxisNode(ArmLogicTreeNode):
    """Translates (moves) the given object using the given vector in the local coordinates."""
    bl_idname = 'LNTranslateOnLocalAxisNode'
    bl_label = 'Translate On Local Axis'
    arm_section = 'location'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmFloatSocket', 'Speed')
        self.add_input('ArmIntSocket', 'Forward/Up/Right')
        self.add_input('ArmBoolSocket', 'Inverse')

        self.add_output('ArmNodeSocketAction', 'Out')
