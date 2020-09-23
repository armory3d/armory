from arm.logicnode.arm_nodes import *

class NavigableLocationNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNNavigableLocationNode'
    bl_label = 'Navigable Location'
    arm_version = 1

    def init(self, context):
        super(NavigableLocationNode, self).init(context)
        self.add_output('NodeSocketShader', 'Location')

add_node(NavigableLocationNode, category=PKG_AS_CATEGORY)
