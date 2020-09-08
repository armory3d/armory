from arm.logicnode.arm_nodes import *

class SetSceneNode(ArmLogicTreeNode):
    """Set scene node"""
    bl_idname = 'LNSetSceneNode'
    bl_label = 'Set Scene'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Scene')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Root')

add_node(SetSceneNode, category=MODULE_AS_CATEGORY)
