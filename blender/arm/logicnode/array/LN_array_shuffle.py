from arm.logicnode.arm_nodes import *

class ArrayShuffleNode(ArmLogicTreeNode):
    """Shuffle the items in the array and return a new array
    """
    bl_idname = 'LNArrayShuffleNode'
    bl_label = 'Array Shuffle'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        
        self.add_output('ArmNodeSocketArray', 'Array')
