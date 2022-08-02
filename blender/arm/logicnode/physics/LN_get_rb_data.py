from arm.logicnode.arm_nodes import *

class GetRigidBodyDataNode(ArmLogicTreeNode):
    """Returns the data of the given rigid body."""
    bl_idname = 'LNGetRigidBodyDataNode'
    bl_label = 'Get RB Data'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')

        self.outputs.new('ArmBoolSocket', 'Is RB')
        self.outputs.new('ArmIntSocket', 'Collision Group')
        self.outputs.new('ArmIntSocket', 'Collision Mask')
        self.outputs.new('ArmBoolSocket', 'Is Animated')
        self.outputs.new('ArmBoolSocket', 'Is Static')
        self.outputs.new('ArmFloatSocket', 'Angular Damping')
        self.outputs.new('ArmFloatSocket', 'Linear Damping')
        self.outputs.new('ArmFloatSocket', 'Friction')
        self.outputs.new('ArmFloatSocket', 'Mass')
        #self.outputs.new('ArmStringSocket', 'Collision Shape')
        #self.outputs.new('ArmIntSocket', 'Activation State')
        #self.outputs.new('ArmBoolSocket', 'Is Gravity Enabled')
        #self.outputs.new(ArmVectorSocket', Angular Factor')
        #self.outputs.new('ArmVectorSocket', Linear Factor')
