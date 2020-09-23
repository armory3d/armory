from arm.logicnode.arm_nodes import *

class CanvasGetRotationNode(ArmLogicTreeNode):
    """Use to get the rotation of an UI element."""
    bl_idname = 'LNCanvasGetRotationNode'
    bl_label = 'Canvas Get Rotation'
    arm_version = 1

    def init(self, context):
        super(CanvasGetRotationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketFloat', 'Rad')

add_node(CanvasGetRotationNode, category=PKG_AS_CATEGORY)
