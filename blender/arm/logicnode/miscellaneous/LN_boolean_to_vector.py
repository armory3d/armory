from arm.logicnode.arm_nodes import *

class VectorFromBooleanNode(ArmLogicTreeNode):
    """Returns a vector depending on the respective boolean state."""
    bl_idname = 'LNVectorFromBooleanNode'
    bl_label = 'Boolean to Vector'
    arm_version = 1

    def init(self, context):
        super(VectorFromBooleanNode, self).init(context)
        self.inputs.new('ArmBoolSocket', 'X')
        self.inputs.new('ArmBoolSocket', '-X')
        self.inputs.new('ArmBoolSocket', 'Y')
        self.inputs.new('ArmBoolSocket', '-Y')
        self.inputs.new('ArmBoolSocket', 'Z')
        self.inputs.new('ArmBoolSocket', '-Z')

        self.outputs.new('ArmVectorSocket', 'Vector')
