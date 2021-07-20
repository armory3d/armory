from arm.logicnode.arm_nodes import *


@deprecated('Set Object Scale')
class ScaleObjectNode(ArmLogicTreeNode):
    """Deprecated. 'Use Set Object Scale' instead."""
    bl_idname = 'LNScaleObjectNode'
    bl_label = 'Scale Object'
    bl_description = "Please use the \"Set Object Scale\" node instead"
    arm_category = 'Transform'
    arm_section = 'scale'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Scale')
        self.add_output('ArmNodeSocketAction', 'Out')
