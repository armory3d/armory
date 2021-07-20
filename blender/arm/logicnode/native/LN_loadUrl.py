from arm.logicnode.arm_nodes import *

class LoadUrlNode(ArmLogicTreeNode):
    """Load the given URL in a new tab (works only for web browsers)."""
    bl_idname = 'LNLoadUrlNode'
    bl_label = 'Load URL'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'URL')
