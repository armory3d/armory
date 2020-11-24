from arm.logicnode.arm_nodes import *

class AppendTransformNode(ArmLogicTreeNode):
    """Appends transform to the given object."""
    bl_idname = 'LNAppendTransformNode'
    bl_label = 'Append Transform'
    arm_version = 1

    def init(self, context):
        super(AppendTransformNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Transform')

        self.add_output('ArmNodeSocketAction', 'Out')
