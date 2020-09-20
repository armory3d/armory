from arm.logicnode.arm_nodes import *

class ColorNode(ArmLogicTreeNode):
    """Color node"""
    bl_idname = 'LNColorNode'
    bl_label = 'Color'
    arm_version = 1

    def init(self, context):
        super(ColorNode, self).init(context)
        self.add_input('NodeSocketColor', 'Color In', default_value=[1, 1, 1, 1])
        self.add_output('NodeSocketColor', 'Color Out', is_var=True)

add_node(ColorNode, category=PKG_AS_CATEGORY)
