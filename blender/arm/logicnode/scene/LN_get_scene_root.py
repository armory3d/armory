from arm.logicnode.arm_nodes import *

class SceneRootNode(ArmLogicTreeNode):
    """The root object of the current scene."""
    bl_idname = 'LNSceneRootNode'
    bl_label = 'Get Scene Root'
    arm_version = 1

    def init(self, context):
        super(SceneRootNode, self).init(context)
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(SceneRootNode, category=PKG_AS_CATEGORY)
