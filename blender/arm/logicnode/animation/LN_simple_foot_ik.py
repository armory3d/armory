from arm.logicnode.arm_nodes import *

class SimpleFootIKNode(ArmLogicTreeNode):
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
    bl_idname = 'LNSimpleFootIKNode'
    bl_label = 'Foot IK Node'
    arm_version = 1
    arm_section = 'armature'

    def update_advanced(self, context):
        self.update_sockets(context)

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimTree', 'Action')
        self.add_input('ArmStringSocket', 'Left Bone')
        self.add_input('ArmStringSocket', 'Right Bone')
        self.add_input('ArmFloatSocket', 'Left Hit Point')
        self.add_input('ArmFloatSocket', 'Right Hit Point')
        self.add_input('ArmFloatSocket', 'Hip Height')
        self.add_input('ArmFloatSocket', 'Foot Offset')
        self.add_input('ArmFloatSocket', 'Foot Offset Threshold')
        self.add_input('ArmFloatSocket', 'Interp Speed', default_value = 0.1)
        self.add_input('ArmIntSocket', 'Bone Group', default_value = 0)

        self.add_output('ArmNodeSocketAnimTree', 'Result')