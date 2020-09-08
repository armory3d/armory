from arm.logicnode.arm_nodes import *

class SelfObjectNode(ArmLogicTreeNode):
    """Returns the object that owns the current trait."""
    bl_idname = 'LNSelfNode'
    bl_label = 'Self Object'

    def init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(SelfObjectNode, category=MODULE_AS_CATEGORY)
