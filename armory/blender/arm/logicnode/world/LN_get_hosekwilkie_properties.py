from arm.logicnode.arm_nodes import *

class GetHosekWilkiePropertiesNode(ArmLogicTreeNode):
    """Gets the HosekWilkie properties."""
    bl_idname = 'LNGetHosekWilkiePropertiesNode'
    bl_label = 'Get HosekWilkie Properties'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Turbidity')
        self.add_output('ArmFloatSocket', 'Ground Albedo')
        self.add_output('ArmVectorSocket', 'Sun Direction')
