from arm.logicnode.arm_nodes import *

class NoneNode(ArmLogicTreeNode):
    """None node"""
    bl_idname = 'LNNoneNode'
    bl_label = 'None'

    def init(self, context):
        self.add_output('NodeSocketShader', 'None')

add_node(NoneNode, category=MODULE_AS_CATEGORY)
