from arm.logicnode.arm_nodes import *

class ArrayDistinctNode(ArmLogicTreeNode):
    """Returns the Distinct and Duplicated items of the given array."""
    bl_idname = 'LNArrayDistinctNode'
    bl_label = 'Array Distinct'
    arm_version = 1
    
    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
       
        self.add_output('ArmNodeSocketArray', 'Distinct')
        self.add_output('ArmNodeSocketArray', 'Duplicated')
