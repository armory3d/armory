from arm.logicnode.arm_nodes import *

class DynamicNode(ArmLogicTreeNode):
    """Stores the given dynamic value (a value with an arbitrary type) as a variable."""
    bl_idname = 'LNDynamicNode'
    bl_label = 'Dynamic'
    arm_version = 1

    def init(self, context):
        super(DynamicNode, self).init(context)
        self.add_output('NodeSocketShader', 'Dynamic', is_var=1)
