from arm.logicnode.arm_nodes import *

class TransformNode(ArmLogicTreeNode):
    """Stores location, rotation, scale values in vector form."""
    bl_idname = 'LNTransformNode'
    bl_label = 'Transform'
    arm_version = 1

    def init(self, context):
        super(TransformNode, self).init(context)
        self.add_input('NodeSocketVector', 'Location')
        self.add_input('NodeSocketVector', 'Rotation')
        self.add_input('NodeSocketVector', 'Scale', default_value=[1.0, 1.0, 1.0])
        self.add_output('NodeSocketShader', 'Transform')

add_node(TransformNode, category=PKG_AS_CATEGORY)
