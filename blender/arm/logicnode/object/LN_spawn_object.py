from arm.logicnode.arm_nodes import *

class SpawnObjectNode(ArmLogicTreeNode):
    """Spawns the given object if present in the current active scene. The spawned object has the same name of its instance, but they are treated as different objects."""

    bl_idname = 'LNSpawnObjectNode'
    bl_label = 'Spawn Object'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Transform')
        self.add_input('ArmBoolSocket', 'Children', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Object')
