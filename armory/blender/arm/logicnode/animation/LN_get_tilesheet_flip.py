from arm.logicnode.arm_nodes import *

class GetTilesheetFlipNode(ArmLogicTreeNode):
    """Returns the flip state of the tilesheet.
    
    @output Flip X: Whether the sprite is flipped horizontally.
    @output Flip Y: Whether the sprite is flipped vertically.
    """
    bl_idname = 'LNGetTilesheetFlipNode'
    bl_label = 'Get Tilesheet Flip'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmBoolSocket', 'Flip X')
        self.add_output('ArmBoolSocket', 'Flip Y')
