from arm.logicnode.arm_nodes import *

class SleepNode(ArmLogicTreeNode):
    """Sleep node"""
    bl_idname = 'LNSleepNode'
    bl_label = 'Sleep'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Time')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SleepNode, category=MODULE_AS_CATEGORY)
