from arm.logicnode.arm_nodes import *

class SetTilesheetFlipNode(ArmLogicTreeNode):
    """Set the flip state of the tilesheet for UV-based sprite flipping.
    This is useful for billboarded sprites where mesh scaling cannot be used.
    
    @input Flip X: Flip the sprite horizontally.
    @input Flip Y: Flip the sprite vertically.
    """
    bl_idname = 'LNSetTilesheetFlipNode'
    bl_label = 'Set Tilesheet Flip'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Flip X')
        self.add_input('ArmBoolSocket', 'Flip Y')

        self.add_output('ArmNodeSocketAction', 'Out')
