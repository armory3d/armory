from arm.logicnode.arm_nodes import *

class CanvasSetTextNode(ArmLogicTreeNode):
    """Use to set the content of an UI text."""
    bl_idname = 'LNCanvasSetTextNode'
    bl_label = 'Canvas Set Text'
    arm_version = 1

    def init(self, context):
        super(CanvasSetTextNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketString', 'Text')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetTextNode, category=PKG_AS_CATEGORY)
