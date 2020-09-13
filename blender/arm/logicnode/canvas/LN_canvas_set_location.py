from arm.logicnode.arm_nodes import *

class CanvasSetLocationNode(ArmLogicTreeNode):
    """Set canvas element location"""
    bl_idname = 'LNCanvasSetLocationNode'
    bl_label = 'Canvas Set Location'
    arm_version = 1

    def init(self, context):
        super(CanvasSetLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'X')
        self.add_input('NodeSocketFloat', 'Y')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetLocationNode, category=PKG_AS_CATEGORY)
