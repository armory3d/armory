from arm.logicnode.arm_nodes import *

class MaskNode(ArmLogicTreeNode):
    """Mask node"""
    bl_idname = 'LNMaskNode'
    bl_label = 'Mask'

    def init(self, context):
        for i in range(1, 21):
            label = 'Group {:02d}'.format(i)
            self.inputs.new('NodeSocketBool', label)

        self.add_output('NodeSocketInt', 'Mask', is_var=True)

add_node(MaskNode, category=MODULE_AS_CATEGORY)
