from arm.logicnode.arm_nodes import *

class VectorFromBooleanNode(ArmLogicTreeNode):
    """Returns a vector depending on the respective boolean state."""
    bl_idname = 'LNVectorFromBooleanNode'
    bl_label = 'Vector From Boolean'
    arm_version = 1

    def init(self, context):
        super(VectorFromBooleanNode, self).init(context)
        self.inputs.new('NodeSocketBool', 'X')
        self.inputs.new('NodeSocketBool', '-X')
        self.inputs.new('NodeSocketBool', 'Y')
        self.inputs.new('NodeSocketBool', '-Y')
        self.inputs.new('NodeSocketBool', 'Z')
        self.inputs.new('NodeSocketBool', '-Z')

        self.outputs.new('NodeSocketVector', 'Vector')
