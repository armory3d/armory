from arm.logicnode.arm_nodes import *

class ArraySampleNode(ArmLogicTreeNode):
    """Take a sample of n items from an array (boolean option to remove those items from original array)
    """
    bl_idname = 'LNArraySampleNode'
    bl_label = 'Array Sample'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Sample')
        self.add_input('ArmBoolSocket', 'Remove')

        self.add_output('ArmNodeSocketArray', 'Array')
