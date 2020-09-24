from arm.logicnode.arm_nodes import *

class CanvasSetCheckBoxNode(ArmLogicTreeNode):
    """Use to set the state of an UI checkbox."""
    bl_idname = 'LNCanvasSetCheckBoxNode'
    bl_label = 'Set Canvas Checkbox'
    arm_version = 1

    def init(self, context):
        super(CanvasSetCheckBoxNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketBool', 'Check')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetCheckBoxNode, category=PKG_AS_CATEGORY)
