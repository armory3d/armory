from arm.logicnode.arm_nodes import *

class CanvasSetRotationNode(ArmLogicTreeNode):
    """Use to set the rotation of an UI element."""
    bl_idname = 'LNCanvasSetRotationNode'
    bl_label = 'Canvas Set Rotation'
    arm_version = 1

    def init(self, context):
        super(CanvasSetRotationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'Rad')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetRotationNode, category=PKG_AS_CATEGORY)
