from arm.logicnode.arm_nodes import *

class LoadUrlNode(ArmLogicTreeNode):
    """Load Url"""
    bl_idname = 'LNLoadUrlNode'
    bl_label = 'Load URL (Browser Only)'
    arm_version = 1

    def init(self, context):
        super(LoadUrlNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'URL')

add_node(LoadUrlNode, category=PKG_AS_CATEGORY)
