from arm.logicnode.arm_nodes import *

class SpawnObjectNode(ArmLogicTreeNode):
    """Spawns the given object. The spawned object has the same name of its instance, but they are threated as different objects."""
    bl_idname = 'LNSpawnObjectNode'
    bl_label = 'Spawn Object'
    arm_version = 1

    def init(self, context):
        super(SpawnObjectNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_input('NodeSocketBool', 'Children', default_value=True)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Object')
