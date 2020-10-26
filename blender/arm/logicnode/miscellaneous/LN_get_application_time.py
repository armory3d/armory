from arm.logicnode.arm_nodes import *

class TimeNode(ArmLogicTreeNode):
    """Returns the application execution time and the delta time."""
    bl_idname = 'LNTimeNode'
    bl_label = 'Get Application Time'
    arm_version = 1

    def init(self, context):
        super(TimeNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Time')
        self.add_output('NodeSocketFloat', 'Delta')

add_node(TimeNode, category=PKG_AS_CATEGORY)
