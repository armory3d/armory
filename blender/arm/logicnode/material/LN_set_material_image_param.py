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
        self.add_input('ArmDynamicSocket', 'Material')
        self.add_input('ArmStringSocket', 'Node')
        self.add_input('ArmStringSocket', 'Image')

        self.add_output('ArmNodeSocketAction', 'Out')
