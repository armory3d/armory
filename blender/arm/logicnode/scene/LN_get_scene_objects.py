from arm.logicnode.arm_nodes import *

class SceneRootNode(ArmLogicTreeNode):
    """Use to get all objects in the scene. Never name a object as 'Root'."""
    bl_idname = 'LNSceneRootNode'
    bl_label = 'Get Scene Objects'
    arm_version = 1

    def init(self, context):
        super(SceneRootNode, self).init(context)
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(SceneRootNode, category=PKG_AS_CATEGORY)
