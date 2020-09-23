from arm.logicnode.arm_nodes import *

class CanvasGetCheckboxNode(ArmLogicTreeNode):
    """Use to get if a UI checkbox is checked."""
    bl_idname = 'LNCanvasGetCheckboxNode'
    bl_label = 'Canvas Get Checkbox'
    arm_version = 1

    def init(self, context):
        super(CanvasGetCheckboxNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketBool', 'Is Checked')

add_node(CanvasGetCheckboxNode, category=PKG_AS_CATEGORY)
