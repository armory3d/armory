from arm.logicnode.arm_nodes import *

class LengthStringNode(ArmLogicTreeNode):
    """String Length node"""
    bl_idname = 'LNLengthStringNode'
    bl_label = 'String Length'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketInt', 'length')
        self.add_input('NodeSocketString', 'String')

add_node(LengthStringNode, category=MODULE_AS_CATEGORY)
