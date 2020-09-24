from arm.logicnode.arm_nodes import *

class AppendTransformNode(ArmLogicTreeNode):
    """Use to append a transform to an object."""
    bl_idname = 'LNAppendTransformNode'
    bl_label = 'Append Transform'
    arm_version = 1

    def init(self, context):
        super(AppendTransformNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(AppendTransformNode, category=PKG_AS_CATEGORY)
