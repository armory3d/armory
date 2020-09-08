from arm.logicnode.arm_nodes import *

class ActiveSceneNode(ArmLogicTreeNode):
    """Active scene node"""
    bl_idname = 'LNActiveSceneNode'
    bl_label = 'Active Scene'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketShader', 'Scene')

add_node(ActiveSceneNode, category=MODULE_AS_CATEGORY)
