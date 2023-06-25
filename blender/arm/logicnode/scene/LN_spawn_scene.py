from arm.logicnode.arm_nodes import *

class SpawnSceneNode(ArmLogicTreeNode):
    """Spawns the given scene."""
    bl_idname = 'LNSpawnSceneNode'
    bl_label = 'Spawn Scene'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Scene')
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Root')
