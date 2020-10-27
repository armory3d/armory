from arm.logicnode.arm_nodes import *

class DisplayInfoNode(ArmLogicTreeNode):
    """Returns the current display resolution.

    @seeNode Get Window Resolution
    """
    bl_idname = 'LNDisplayInfoNode'
    bl_label = 'Get Display Resolution'
    arm_section = 'screen'
    arm_version = 1

    def init(self, context):
        super(DisplayInfoNode, self).init(context)
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')
