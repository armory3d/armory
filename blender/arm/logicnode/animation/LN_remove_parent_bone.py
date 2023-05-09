from arm.logicnode.arm_nodes import *

class RemoveParentBoneNode(ArmLogicTreeNode):
    """Removes the given object parent to the given bone."""
    bl_idname = 'LNRemoveParentBoneNode'
    bl_label = 'Remove Parent Bone'
    arm_version = 1
    arm_section = 'armature'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Parent')
        self.add_input('ArmStringSocket', 'Bone', default_value='Bone')

        self.add_output('ArmNodeSocketAction', 'Out')
