from arm.logicnode.arm_nodes import *

class SetMaterialNode(ArmLogicTreeNode):
    """Set material node"""
    bl_idname = 'LNSetMaterialNode'
    bl_label = 'Set Material'
    arm_version = 1

    def init(self, context):
        super(SetMaterialNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Material')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMaterialNode, category=PKG_AS_CATEGORY)
