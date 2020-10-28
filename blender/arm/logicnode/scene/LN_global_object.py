from arm.logicnode.arm_nodes import *

class GlobalObjectNode(ArmLogicTreeNode):
    """Gives access to a global object which can be used to share
    information between different traits."""
    bl_idname = 'LNGlobalObjectNode'
    bl_label = 'Global Object'
    arm_version = 1

    def init(self, context):
        super(GlobalObjectNode, self).init(context)
        self.add_output('ArmNodeSocketObject', 'Object')
