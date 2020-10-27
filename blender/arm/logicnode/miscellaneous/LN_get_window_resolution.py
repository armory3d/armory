from arm.logicnode.arm_nodes import *

class WindowInfoNode(ArmLogicTreeNode):
    """Returns the current window resolution.

    @seeNode Get Display Resolution
    """
    bl_idname = 'LNWindowInfoNode'
    bl_label = 'Get Window Resolution'
    arm_section = 'screen'
    arm_version = 1

    def init(self, context):
        super(WindowInfoNode, self).init(context)
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')
