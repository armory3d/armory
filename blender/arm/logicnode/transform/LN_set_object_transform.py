from arm.logicnode.arm_nodes import *

class SetTransformNode(ArmLogicTreeNode):
    """Use to set the transform of an object."""
    bl_idname = 'LNSetTransformNode'
    bl_label = 'Set Object Transform'
    arm_version = 1

    def init(self, context):
        super(SetTransformNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetTransformNode, category=PKG_AS_CATEGORY)
