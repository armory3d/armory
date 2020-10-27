from arm.logicnode.arm_nodes import *

class GetMaterialNode(ArmLogicTreeNode):
    """Returns the material of the given object."""
    bl_idname = 'LNGetMaterialNode'
    bl_label = 'Get Object Material'
    arm_version = 1

    def init(self, context):
        super(GetMaterialNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketInt', 'Slot')
        self.add_output('NodeSocketShader', 'Material')
