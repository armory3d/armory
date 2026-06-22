from arm.logicnode.arm_nodes import *

class SetParticleRenderEmitterNode(ArmLogicTreeNode):
    """Sets the Render Emitter of the given particle source."""
    bl_idname = 'LNSetParticleRenderEmitterNode'
    bl_label = 'Set Particle Render Emitter'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Render Emitter', default_value = True)

        self.add_output('ArmNodeSocketAction', 'Out')