from arm.logicnode.arm_nodes import *

class SetMaterialTextureFilterNode(ArmLogicTreeNode):
    """Sets texture filter interpolation."""
    bl_idname = 'LNSetMaterialTextureFilterNode'
    bl_label = 'Set Object Material Texture Filter'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Material')
        self.add_input('ArmIntSocket', 'Slot')
        self.add_input('ArmStringSocket', 'Node')
        self.add_input('ArmIntSocket', 'Texture Filter')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.label(text='Tex Filter 0: Linear')
        layout.label(text='Tex Filter 1: Closest')
        layout.label(text='Tex Filter 2: Cubic')
        layout.label(text='Tex Filter 3: Smart')
