from arm.logicnode.arm_nodes import *


@deprecated('Set Object Material Slot')
class SetMaterialNode(ArmLogicTreeNode):
    """Sets the material of the given object."""
    bl_idname = 'LNSetMaterialNode'
    bl_label = 'Set Object Material'
    bl_description = "Please use the \"Set Object Material Slot\" node instead"
    arm_category = 'Material'
    arm_version = 2

    def init(self, context):
        super(SetMaterialNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Material')
        self.add_output('ArmNodeSocketAction', 'Out')
