from arm.logicnode.arm_nodes import *

class GetInputMapKeyNode(ArmLogicTreeNode):
    """Get key data if it exists in the input map."""
    bl_idname = 'LNGetInputMapKeyNode'
    bl_label = 'Get Input Map Key'
    arm_version = 1

    def init(self, context):
        super(GetInputMapKeyNode, self).init(context)
        self.add_input('NodeSocketString', 'Input Map')
        self.add_input('NodeSocketString', 'Key')

        self.add_output('NodeSocketFloat', 'Scale', default_value = 1.0)
        self.add_output('NodeSocketFloat', 'Deadzone')