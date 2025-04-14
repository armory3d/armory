from arm.logicnode.arm_nodes import *

class SceneRootNode(ArmLogicTreeNode):
    """Returns the root object of the current scene."""
    bl_idname = 'LNSceneRootNode'
    bl_label = 'Get Scene Root'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')
