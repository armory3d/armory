from arm.logicnode.arm_nodes import *

class CanvasGetInputTextNode(ArmLogicTreeNode):
    """Returns the input text of the given UI element."""
    bl_idname = 'LNCanvasGetInputTextNode'
    bl_label = 'Get Canvas Input Text'
    arm_version = 1

    def init(self, context):
        super(CanvasGetInputTextNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketString', 'Text')

add_node(CanvasGetInputTextNode, category=PKG_AS_CATEGORY)
