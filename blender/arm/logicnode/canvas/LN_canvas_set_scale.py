from arm.logicnode.arm_nodes import *

class CanvasSetScaleNode(ArmLogicTreeNode):
    """Set canvas element scale"""
    bl_idname = 'LNCanvasSetScaleNode'
    bl_label = 'Canvas Set Scale'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketInt', 'Height')
        self.add_input('NodeSocketInt', 'Width')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetScaleNode, category=PKG_AS_CATEGORY)
