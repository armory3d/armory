from arm.logicnode.arm_nodes import *

class LengthStringNode(ArmLogicTreeNode):
    """Returns the length of the given string."""
    bl_idname = 'LNLengthStringNode'
    bl_label = 'String Length'
    arm_version = 1

    def init(self, context):
        super(LengthStringNode, self).init(context)
        self.add_output('NodeSocketInt', 'Length')
        self.add_input('NodeSocketString', 'String')

add_node(LengthStringNode, category=PKG_AS_CATEGORY)
