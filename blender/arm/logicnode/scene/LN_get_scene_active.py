from arm.logicnode.arm_nodes import *

class ActiveSceneNode(ArmLogicTreeNode):
    """Get the active scene."""
    bl_idname = 'LNActiveSceneNode'
    bl_label = 'Get Scene Active'
    arm_version = 1

    def init(self, context):
        super(ActiveSceneNode, self).init(context)
        self.add_output('NodeSocketShader', 'Scene')

add_node(ActiveSceneNode, category=PKG_AS_CATEGORY)
