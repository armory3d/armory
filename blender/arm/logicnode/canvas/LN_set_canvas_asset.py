from arm.logicnode.arm_nodes import *

class CanvasSetAssetNode(ArmLogicTreeNode):
    """Sets the asset of the given UI element."""
    bl_idname = 'LNCanvasSetAssetNode'
    bl_label = 'Set Canvas Asset'
    arm_version = 1

    def init(self, context):
        super(CanvasSetAssetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketString', 'Asset')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetAssetNode, category=PKG_AS_CATEGORY)
