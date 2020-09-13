from arm.logicnode.arm_nodes import *

class SleepNode(ArmLogicTreeNode):
    """Sleep node"""
    bl_idname = 'LNSleepNode'
    bl_label = 'Sleep'
    arm_version = 1

    def init(self, context):
        super(SleepNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Time')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SleepNode, category=PKG_AS_CATEGORY)
