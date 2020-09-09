from arm.logicnode.arm_nodes import *

class ClearParentNode(ArmLogicTreeNode):
    """Clear parent node"""
    bl_idname = 'LNClearParentNode'
    bl_label = 'Clear Parent'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketBool', 'Keep Transform', default_value=True)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ClearParentNode, category=PKG_AS_CATEGORY, section='relations')

