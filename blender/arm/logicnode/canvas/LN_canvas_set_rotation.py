from arm.logicnode.arm_nodes import *

class CanvasSetRotationNode(ArmLogicTreeNode):
    """Set canvas element rotation"""
    bl_idname = 'LNCanvasSetRotationNode'
    bl_label = 'Canvas Set Rotation'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'Rad')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetRotationNode, category=PKG_AS_CATEGORY)
