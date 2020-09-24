from arm.logicnode.arm_nodes import *

class ColorNode(ArmLogicTreeNode):
    """Use to hold a color as a variable."""
    bl_idname = 'LNColorNode'
    bl_label = 'Color'
    arm_version = 1

    def init(self, context):
        super(ColorNode, self).init(context)
        self.add_input('NodeSocketColor', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_output('NodeSocketColor', 'Color Out', is_var=True)

add_node(ColorNode, category=PKG_AS_CATEGORY)
