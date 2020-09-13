from arm.logicnode.arm_nodes import *

class CanvasGetRotationNode(ArmLogicTreeNode):
    """Get canvas element rotation"""
    bl_idname = 'LNCanvasGetRotationNode'
    bl_label = 'Canvas Get Rotation'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketFloat', 'Rad')

add_node(CanvasGetRotationNode, category=PKG_AS_CATEGORY)
