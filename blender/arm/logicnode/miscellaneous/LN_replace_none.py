from arm.logicnode.arm_nodes import *

class ReplaceNoneNode(ArmLogicTreeNode):
    """Returns the ´value 1´ if it is not ´null´, otherwise the ´value 2´ will be returned."""
    bl_idname = 'LNReplaceNoneNode'
    bl_label = 'Replace None'
    arm_version = 1

    def init(self, context):
        super(ReplaceNoneNode, self).init(context)
        self.inputs.new('NodeSocketShader', 'Value 1')
        self.inputs.new('NodeSocketShader', 'Value 2')
        self.outputs.new('NodeSocketShader', 'Value')
