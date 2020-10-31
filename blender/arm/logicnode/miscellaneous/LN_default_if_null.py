from arm.logicnode.arm_nodes import *

class DefaultIfNullNode(ArmLogicTreeNode):
    """Returns the value in `Value In` if it is not `null`, otherwise the value in `Default` will be returned."""
    bl_idname = 'LNDefaultIfNullNode'
    bl_label = 'Default If Null'
    arm_version = 1

    def init(self, context):
        super(DefaultIfNullNode, self).init(context)
        self.inputs.new('NodeSocketShader', 'Value In')
        self.inputs.new('NodeSocketShader', 'Default')
        self.outputs.new('NodeSocketShader', 'Value Out')
