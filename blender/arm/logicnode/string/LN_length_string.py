from arm.logicnode.arm_nodes import *

class LengthStringNode(ArmLogicTreeNode):
    """String Length node"""
    bl_idname = 'LNLengthStringNode'
    bl_label = 'String Length'
    arm_version = 1

    def init(self, context):
        super(LengthStringNode, self).init(context)
        self.add_output('NodeSocketInt', 'length')
        self.add_input('NodeSocketString', 'String')

add_node(LengthStringNode, category=PKG_AS_CATEGORY)
