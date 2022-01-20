from arm.logicnode.arm_nodes import *

class ArrayShuffleNode(ArmLogicTreeNode):
    """to do
    """
    bl_idname = 'LNArrayShuffleNode'
    bl_label = 'Array Shuffle'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        
        self.add_output('ArmNodeSocketArray', 'Array')