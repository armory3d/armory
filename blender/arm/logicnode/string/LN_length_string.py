from arm.logicnode.arm_nodes import *

class LengthStringNode(ArmLogicTreeNode):
    """String Length node"""
    bl_idname = 'LNLengthStringNode'
    bl_label = 'String Length'

    def init(self, context):
        self.add_output('NodeSocketInt', 'length')
        self.add_input('NodeSocketString', 'String')

add_node(LengthStringNode, category=PKG_AS_CATEGORY)
