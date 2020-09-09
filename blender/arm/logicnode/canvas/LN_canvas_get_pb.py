from arm.logicnode.arm_nodes import *

class CanvasGetPBNode(ArmLogicTreeNode):
    """Get canvas progress bar"""
    bl_idname = 'LNCanvasGetPBNode'
    bl_label = 'Canvas Get Progress Bar'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketInt', 'At')
        self.add_output('NodeSocketInt', 'Max')

add_node(CanvasGetPBNode, category=PKG_AS_CATEGORY)
