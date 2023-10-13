from arm.logicnode.arm_nodes import *

class HideActiveCanvas(ArmLogicTreeNode):
    """HideActiveCanvas"""
    bl_idname = 'LNHideActiveCanvas'
    bl_label = 'Hide Active Canvas'
    bl_description = 'This node Hides and shows the whole Active Canvas'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.inputs.new('ArmBoolSocket', 'HideCanvas')