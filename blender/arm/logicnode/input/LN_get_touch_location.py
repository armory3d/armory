from arm.logicnode.arm_nodes import *

class GetTouchLocationNode(ArmLogicTreeNode):
    """Returns the location of the last touch event in screen coordinates (pixels)."""
    bl_idname = 'LNGetTouchLocationNode'
    bl_label = 'Get Touch Location'
    arm_version = 1

    def init(self, context):
        super(GetTouchLocationNode, self).init(context)
        self.add_output('NodeSocketInt', 'X')
        self.add_output('NodeSocketInt', 'Y')
        self.add_output('NodeSocketInt', 'Inverted X')
        self.add_output('NodeSocketInt', 'Inverted Y')

add_node(GetTouchLocationNode, category=PKG_AS_CATEGORY, section='surface')
