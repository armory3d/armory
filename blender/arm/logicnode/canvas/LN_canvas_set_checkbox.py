from arm.logicnode.arm_nodes import *

class CanvasSetCheckBoxNode(ArmLogicTreeNode):
    """Set canvas check box"""
    bl_idname = 'LNCanvasSetCheckBoxNode'
    bl_label = 'Canvas Set Checkbox'
    arm_version = 1

    def init(self, context):
        super(CanvasSetCheckBoxNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketBool', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetCheckBoxNode, category=PKG_AS_CATEGORY)
