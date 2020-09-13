from arm.logicnode.arm_nodes import *

class SpawnSceneNode(ArmLogicTreeNode):
    """Spawn scene node"""
    bl_idname = 'LNSpawnSceneNode'
    bl_label = 'Spawn Scene'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Scene')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Root')

add_node(SpawnSceneNode, category=PKG_AS_CATEGORY)
