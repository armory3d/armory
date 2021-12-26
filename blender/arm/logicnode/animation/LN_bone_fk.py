from arm.logicnode.arm_nodes import *

class BoneFKNode(ArmLogicTreeNode):
    """Applies forward kinematics in the given object bone."""
    bl_idname = 'LNBoneFKNode'
    bl_label = 'Bone FK'
    arm_version = 2
    arm_section = 'armature'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimTree', 'Action Tree')
        self.add_input('ArmStringSocket', 'Bone')
        self.add_input('ArmDynamicSocket', 'Transform')
        self.add_output('ArmNodeSocketAnimTree', 'Action Tree')