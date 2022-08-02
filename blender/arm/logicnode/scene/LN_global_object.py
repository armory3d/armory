from arm.logicnode.arm_nodes import *

class GlobalObjectNode(ArmLogicTreeNode):
    """Gives access to a global object which can be used to share
    information between different traits."""
    bl_idname = 'LNGlobalObjectNode'
    bl_label = 'Global Object'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')
