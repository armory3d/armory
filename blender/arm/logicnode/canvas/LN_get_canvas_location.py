from arm.logicnode.arm_nodes import *

class CanvasGetLocationNode(ArmLogicTreeNode):
    """Returns the location of the given UI element (pixels)."""
    bl_idname = 'LNCanvasGetLocationNode'
    bl_label = 'Get Canvas Location'
    arm_version = 1

    def init(self, context):
        super(CanvasGetLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketInt', 'X')
        self.add_output('NodeSocketInt', 'Y')

add_node(CanvasGetLocationNode, category=PKG_AS_CATEGORY)
