from arm.logicnode.arm_nodes import *

class GetNishitaPropertiesNode(ArmLogicTreeNode):
    """Gets the Nishita properties."""
    bl_idname = 'LNGetNishitaPropertiesNode'
    bl_label = 'Get Nishita Properties'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Air')
        self.add_output('ArmFloatSocket', 'Dust')
        self.add_output('ArmFloatSocket', 'Ozone')
        self.add_output('ArmVectorSocket', 'Sun Direction')

