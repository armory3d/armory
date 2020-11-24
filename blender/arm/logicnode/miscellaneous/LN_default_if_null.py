from arm.logicnode.arm_nodes import *

class DefaultIfNullNode(ArmLogicTreeNode):
    """Returns the connected value only if it is not `null`, otherwise the `default` value is returned.

    @input Value: the one that will be eventually null
    @input Default: will be returned in case the primary value is null
    """
    bl_idname = 'LNDefaultIfNullNode'
    bl_label = 'Default if Null'
    arm_version = 1

    def init(self, context):
        super(DefaultIfNullNode, self).init(context)
        self.inputs.new('NodeSocketShader', 'Value In')
        self.inputs.new('NodeSocketShader', 'Default')

        self.outputs.new('NodeSocketShader', 'Value Out')
