from arm.logicnode.arm_nodes import *

class CanvasGetCheckboxNode(ArmLogicTreeNode):
    """Get canvas checkbox value"""
    bl_idname = 'LNCanvasGetCheckboxNode'
    bl_label = 'Canvas Get Checkbox'

    def init(self, context):
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketBool', 'Value')

add_node(CanvasGetCheckboxNode, category=MODULE_AS_CATEGORY)
