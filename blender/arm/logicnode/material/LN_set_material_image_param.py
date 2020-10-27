from arm.logicnode.arm_nodes import *

class SetMaterialImageParamNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNSetMaterialImageParamNode'
    bl_label = 'Set Material Image Param'
    arm_section = 'params'
    arm_version = 1

    def init(self, context):
        super(SetMaterialImageParamNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketString', 'Image')
        self.add_output('ArmNodeSocketAction', 'Out')
