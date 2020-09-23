from arm.logicnode.arm_nodes import *

class CanvasGetInputTextNode(ArmLogicTreeNode):
    """Use to get the input text of an UI element."""
    bl_idname = 'LNCanvasGetInputTextNode'
    bl_label = 'Canvas Get Input Text'
    arm_version = 1

    def init(self, context):
        super(CanvasGetInputTextNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketString', 'String')

add_node(CanvasGetInputTextNode, category=PKG_AS_CATEGORY)
