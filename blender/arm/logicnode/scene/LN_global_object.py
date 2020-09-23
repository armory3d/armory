from arm.logicnode.arm_nodes import *

class GlobalObjectNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNGlobalObjectNode'
    bl_label = 'Global Object'
    arm_version = 1

    def init(self, context):
        super(GlobalObjectNode, self).init(context)
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(GlobalObjectNode, category=PKG_AS_CATEGORY)
