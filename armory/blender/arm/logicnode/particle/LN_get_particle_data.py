from arm.logicnode.arm_nodes import *

class GetParticleDataNode(ArmLogicTreeNode):
    """Returns the data of the given Particle System."""
    bl_idname = 'LNGetParticleDataNode'
    bl_label = 'Get Particle Data'
    arm_version = 1

    def arm_init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmIntSocket', 'Slot')

        self.outputs.new('ArmStringSocket', 'Name')
        self.outputs.new('ArmFloatSocket', 'Particle Size')
        self.outputs.new('ArmIntSocket', 'Frame Start')
        self.outputs.new('ArmIntSocket', 'Frame End')
        self.outputs.new('ArmIntSocket', 'Lifetime')
        self.outputs.new('ArmFloatSocket', 'Lifetime Random')
        self.outputs.new('ArmIntSocket', 'Emit From')

        self.outputs.new('ArmVectorSocket', 'Velocity')
        self.outputs.new('ArmFloatSocket', 'Velocity Random')
        self.outputs.new('ArmVectorSocket', 'Gravity')
        self.outputs.new('ArmFloatSocket', 'Weight Gravity')

        self.outputs.new('ArmFloatSocket', 'Speed')
    
        self.outputs.new('ArmFloatSocket', 'Time')
        self.outputs.new('ArmFloatSocket', 'Lap')
        self.outputs.new('ArmFloatSocket', 'Lap Time')
        self.outputs.new('ArmIntSocket', 'Count')
