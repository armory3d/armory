from arm.logicnode.arm_nodes import *

class DynamicNode(ArmLogicTreeNode):
    """Use to hold a dynamic value as a variable."""
    bl_idname = 'LNDynamicNode'
    bl_label = 'Dynamic'
    arm_version = 1

    def init(self, context):
        super(DynamicNode, self).init(context)
        self.add_output('NodeSocketShader', 'Dynamic', is_var=True)

add_node(DynamicNode, category=PKG_AS_CATEGORY)
