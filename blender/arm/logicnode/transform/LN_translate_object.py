from arm.logicnode.arm_nodes import *

class TranslateObjectNode(ArmLogicTreeNode):
    """Translates (moves) the given object using the given vector in world coordinates."""
    bl_idname = 'LNTranslateObjectNode'
    bl_label = 'Translate Object'
    arm_section = 'location'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Vector')
        self.add_input('ArmBoolSocket', 'On Local Axis')

        self.add_output('ArmNodeSocketAction', 'Out')
