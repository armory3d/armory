from arm.logicnode.arm_nodes import *

class CanvasGetLocationNode(ArmLogicTreeNode):
    """Get canvas element location"""
    bl_idname = 'LNCanvasGetLocationNode'
    bl_label = 'Canvas Get Location'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')

add_node(CanvasGetLocationNode, category=MODULE_AS_CATEGORY)
