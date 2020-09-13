from arm.logicnode.arm_nodes import *

class SceneRootNode(ArmLogicTreeNode):
    """Scene root node"""
    bl_idname = 'LNSceneRootNode'
    bl_label = 'Scene Root'

    def init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(SceneRootNode, category=PKG_AS_CATEGORY)
