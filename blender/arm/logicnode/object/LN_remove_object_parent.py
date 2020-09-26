from arm.logicnode.arm_nodes import *

class ClearParentNode(ArmLogicTreeNode):
    """Use to remove the parent of an object."""
    bl_idname = 'LNClearParentNode'
    bl_label = 'Remove Object Parent'
    arm_version = 1

    def init(self, context):
        super(ClearParentNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketBool', 'Keep Transform', default_value=True)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ClearParentNode, category=PKG_AS_CATEGORY, section='relations')

