from arm.logicnode.arm_nodes import *

class GetTransformNode(ArmLogicTreeNode):
    """Use to get the transform of an object."""
    bl_idname = 'LNGetTransformNode'
    bl_label = 'Get Transform'
    arm_version = 1

    def init(self, context):
        super(GetTransformNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketShader', 'Transform')

add_node(GetTransformNode, category=PKG_AS_CATEGORY)
