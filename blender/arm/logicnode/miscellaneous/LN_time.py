from arm.logicnode.arm_nodes import *

class TimeNode(ArmLogicTreeNode):
    """Time node"""
    bl_idname = 'LNTimeNode'
    bl_label = 'Time'
    arm_version = 1

    def init(self, context):
        super(TimeNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Time')
        self.add_output('NodeSocketFloat', 'Delta')

add_node(TimeNode, category=PKG_AS_CATEGORY)
