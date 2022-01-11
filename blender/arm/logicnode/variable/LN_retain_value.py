from arm.logicnode.arm_nodes import *

class RetainValueNode(ArmLogicTreeNode):
    """Retains the input value

    @input Retain: Retains the value when exeuted.
    @input Value: The value that should be retained.
    """
    bl_idname = 'LNRetainValueNode'
    bl_label = 'Retain Value'
    arm_section = 'set'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Retain')
        self.add_input('ArmDynamicSocket', 'Value', is_var=True)

        self.add_output('ArmDynamicSocket', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')
