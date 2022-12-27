from arm.logicnode.arm_nodes import *

class StringReplaceNode(ArmLogicTreeNode):
    """Replace all ocurrences of x in Strings"""
    bl_idname = 'LNStringReplaceNode'
    bl_label = 'String Replace'

    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmStringSocket', 'Find')
        self.add_input('ArmStringSocket', 'Replace')
        
        self.add_output('ArmIntSocket', 'String')
