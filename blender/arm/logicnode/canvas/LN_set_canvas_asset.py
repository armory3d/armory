from arm.logicnode.arm_nodes import *

class CanvasSetAssetNode(ArmLogicTreeNode):
    """Sets the asset of the given UI element."""
    bl_idname = 'LNCanvasSetAssetNode'
    bl_label = 'Set Canvas Asset'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmStringSocket', 'Asset')

        self.add_output('ArmNodeSocketAction', 'Out')
