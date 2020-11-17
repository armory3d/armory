from arm.logicnode.arm_nodes import *

class MaskNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNMaskNode'
    bl_label = 'Mask'
    arm_version = 1

    def init(self, context):
        super(MaskNode, self).init(context)
        for i in range(1, 21):
            label = 'Group {:02d}'.format(i)
            self.inputs.new('NodeSocketBool', label)

        self.add_output('NodeSocketInt', 'Mask', is_var=1)
