from arm.logicnode.arm_nodes import *

class GetParticleNode(ArmLogicTreeNode):
    """Returns the Particle Systems of an object."""
    bl_idname = 'LNGetParticleNode'
    bl_label = 'Get Particle'
    arm_version = 1

    def arm_init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')

        self.outputs.new('ArmNodeSocketArray', 'Names')
        self.outputs.new('ArmIntSocket', 'Length')
        self.outputs.new('ArmBoolSocket', 'Render Emitter')
        
