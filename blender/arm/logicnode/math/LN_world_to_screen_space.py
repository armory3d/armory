from arm.logicnode.arm_nodes import *

class WorldToScreenSpaceNode(ArmLogicTreeNode):
    """Transforms the given world coordinates into screen coordinates."""
    bl_idname = 'LNWorldToScreenSpaceNode'
    bl_label = 'World To Screen Space'
    arm_version = 1

    def init(self, context):
        super(WorldToScreenSpaceNode, self).init(context)
        self.add_input('NodeSocketVector', 'World')
        self.add_output('NodeSocketVector', 'Screen')

add_node(WorldToScreenSpaceNode, category=PKG_AS_CATEGORY, section='matrix')
