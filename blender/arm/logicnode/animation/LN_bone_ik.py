from arm.logicnode.arm_nodes import *

class BoneIKNode(ArmLogicTreeNode):
    """Performs inverse kinematics on the selected armature with specified bone.
    
    @input Object: Armature on which IK should be performed.

    @input Bone: Effector or tip bone for the inverse kinematics

    @input Goal Position: Position in world coordinates the effector bone will track to

    @input Enable Pole: Bend IK solution towards pole location

    @input Pole Position: Location of the pole in world coordinates

    @input Chain Length: Number of bones to include in the IK solver including the effector. If set to 0, all bones from effector to the root bone of the armature will be considered.
    
    @input Max Iterations: Maximum allowed FABRIK iterations to solve for IK. For longer chains, more iterations are needed.

    @input Precision: Presition of IK to stop at. It is described as a tolerence in length. Typically 0.01 is a good value.

    @input Roll Angle: Roll the bones along their local axis with specified radians. set 0 for no extra roll.
    """
    bl_idname = 'LNBoneIKNode'
    bl_label = 'Bone IK'
    arm_version = 2
    arm_section = 'armature'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Bone')
        self.add_input('ArmVectorSocket', 'Goal Position')
        self.add_input('ArmBoolSocket', 'Enable Pole')
        self.add_input('ArmVectorSocket', 'Pole Position')
        self.add_input('ArmIntSocket', 'Chain Length')
        self.add_input('ArmIntSocket', 'Max Iterations', 10)
        self.add_input('ArmFloatSocket', 'Precision', 0.01)
        self.add_input('ArmFloatSocket', 'Roll Angle')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
        
        return NodeReplacement(
            'LNBoneIKNode', self.arm_version, 'LNBoneIKNode', 2,
            in_socket_mapping={0:0, 1:1, 2:2, 3:3}, out_socket_mapping={0:0}
        )
