from arm.logicnode.arm_nodes import *

class ResolutionSetNode(ArmLogicTreeNode):
    """Set the resolution post-processing settings.
    Filter 0: Lineal 1: Closest
    """
    bl_idname = 'LNResolutionSetNode'
    bl_label = 'Set Resolution Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmIntSocket', 'Size', default_value=720)
        self.add_input('ArmIntSocket', 'Filter', default_value=0)

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.label(text="Type 0: Lineal")
        layout.label(text="Type 1: Closest")
