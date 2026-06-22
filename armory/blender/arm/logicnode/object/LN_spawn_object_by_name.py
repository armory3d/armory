from arm.logicnode.arm_nodes import *

class SpawnObjectByNameNode(ArmLogicTreeNode):
    """Spawns an object bearing the given name, even if not present in the active scene"""
    bl_idname = 'LNSpawnObjectByNameNode'
    bl_label = 'Spawn Object By Name'
    arm_version = 1

    property0: HaxePointerProperty(
        'property0',
        type=bpy.types.Scene, name='Scene',
        description='The scene from which to take the object')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Name')
        self.add_input('ArmDynamicSocket', 'Transform')
        self.add_input('ArmBoolSocket', 'Children', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Object')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, "scenes")
