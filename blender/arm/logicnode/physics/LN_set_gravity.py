from arm.logicnode.arm_nodes import *

class SetGravityNode(ArmLogicTreeNode):
    """Set Gravity node"""
    bl_idname = 'LNSetGravityNode'
    bl_label = 'Set Gravity'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketVector', 'Gravity')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetGravityNode, category=PKG_AS_CATEGORY)
