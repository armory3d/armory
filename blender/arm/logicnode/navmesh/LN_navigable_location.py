from arm.logicnode.arm_nodes import *

class NavigableLocationNode(ArmLogicTreeNode):
    """Navigable location node"""
    bl_idname = 'LNNavigableLocationNode'
    bl_label = 'Navigable Location'

    def init(self, context):
        self.add_output('NodeSocketShader', 'Location')

add_node(NavigableLocationNode, category=PKG_AS_CATEGORY)
