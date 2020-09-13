from arm.logicnode.arm_nodes import *

class SeparateTransformNode(ArmLogicTreeNode):
    """Separate transform node"""
    bl_idname = 'LNSeparateTransformNode'
    bl_label = 'Separate Transform'
    arm_version = 1

    def init(self, context):
        super(SeparateTransformNode, self).init(context)
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('NodeSocketVector', 'Location')
        self.add_output('NodeSocketVector', 'Rotation')
        self.add_output('NodeSocketVector', 'Scale')

add_node(SeparateTransformNode, category=PKG_AS_CATEGORY)
