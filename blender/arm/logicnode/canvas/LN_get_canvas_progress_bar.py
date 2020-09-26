from arm.logicnode.arm_nodes import *

class CanvasGetPBNode(ArmLogicTreeNode):
    """Use to get the value of an UI progress bar."""
    bl_idname = 'LNCanvasGetPBNode'
    bl_label = 'Get Canvas Progress Bar'
    arm_version = 1

    def init(self, context):
        super(CanvasGetPBNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketInt', 'At')
        self.add_output('NodeSocketInt', 'Max')

add_node(CanvasGetPBNode, category=PKG_AS_CATEGORY)
