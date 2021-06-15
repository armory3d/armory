from arm.logicnode.arm_nodes import *

class TransformNode(ArmLogicTreeNode):
    """Stores the location, rotation and scale values as a transform."""
    bl_idname = 'LNTransformNode'
    bl_label = 'Transform'
    arm_version = 1

    def init(self, context):
        super(TransformNode, self).init(context)
        self.add_input('NodeSocketVector', 'Location')
        self.add_input('ArmNodeSocketRotation', 'Rotation')
        self.add_input('NodeSocketVector', 'Scale', default_value=[1.0, 1.0, 1.0])

        self.add_output('NodeSocketShader', 'Transform', is_var=True)
