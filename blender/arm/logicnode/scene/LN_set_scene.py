from arm.logicnode.arm_nodes import *

class SetSceneNode(ArmLogicTreeNode):
    """Set scene node"""
    bl_idname = 'LNSetSceneNode'
    bl_label = 'Set Scene'
    arm_version = 1

    def init(self, context):
        super(SetSceneNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Scene')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Root')

add_node(SetSceneNode, category=PKG_AS_CATEGORY)
