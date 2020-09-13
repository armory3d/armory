from arm.logicnode.arm_nodes import *

class CanvasSetAssetNode(ArmLogicTreeNode):
    """Set canvas asset"""
    bl_idname = 'LNCanvasSetAssetNode'
    bl_label = 'Canvas Set Asset'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketString', 'Asset')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetAssetNode, category=PKG_AS_CATEGORY)
