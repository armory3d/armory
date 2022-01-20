from arm.logicnode.arm_nodes import *

class ArraySampleNode(ArmLogicTreeNode):
    """to do
    """
    bl_idname = 'LNArraySampleNode'
    bl_label = 'Array Sample'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Sample')
        self.add_input('ArmBoolSocket', 'remove')

        self.add_output('ArmNodeSocketArray', 'Array')