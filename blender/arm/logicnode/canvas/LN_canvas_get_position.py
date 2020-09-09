from arm.logicnode.arm_nodes import *

class CanvasGetPositionNode(ArmLogicTreeNode):
    """Get canvas radio and combo value"""
    bl_idname = 'LNCanvasGetPositionNode'
    bl_label = 'Canvas Get Position'

    def init(self, context):
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketInt', 'Value')

add_node(CanvasGetPositionNode, category=PKG_AS_CATEGORY)
