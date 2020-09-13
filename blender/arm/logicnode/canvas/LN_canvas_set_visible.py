from arm.logicnode.arm_nodes import *

class CanvasSetVisibleNode(ArmLogicTreeNode):
    """Canvas Set Visible node"""
    bl_idname = 'LNCanvasSetVisibleNode'
    bl_label = 'Canvas Set Visible'
    arm_version = 1

    def init(self, context):
        super(CanvasSetVisibleNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketBool', 'Visible')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetVisibleNode, category=PKG_AS_CATEGORY)
