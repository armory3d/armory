from arm.logicnode.arm_nodes import *

class ArrayCountNode(ArmLogicTreeNode):
    """Returns an array with the item counts of the given array."""
    bl_idname = 'LNArrayCountNode'
    bl_label = 'Array Count'
    arm_version = 1
    
    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
       
        self.add_output('ArmNodeSocketArray', 'Count')
