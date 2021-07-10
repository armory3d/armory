from arm.logicnode.arm_nodes import *

class SetParticleSpeedNode(ArmLogicTreeNode):
    """Sets the speed of the given particle source."""
    bl_idname = 'LNSetParticleSpeedNode'
    bl_label = 'Set Particle Speed'
    arm_version = 1

    def init(self, context):
        super(SetParticleSpeedNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmFloatSocket', 'Speed', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')
