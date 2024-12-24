from arm.logicnode.arm_nodes import *

class IntFromBooleanNode(ArmLogicTreeNode):
    """Returns an int depending on the respective boolean state."""
    bl_idname = 'LNIntFromBooleanNode'
    bl_label = 'Boolean to Int'
    arm_version = 1

    def arm_init(self, context):
        self.inputs.new('ArmBoolSocket', 'Bool')

        self.outputs.new('ArmIntSocket', 'Int')
