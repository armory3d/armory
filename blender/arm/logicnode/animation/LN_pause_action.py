from arm.logicnode.arm_nodes import *

class PauseActionNode(ArmLogicTreeNode):
    """Pause action node"""
    bl_idname = 'LNPauseActionNode'
    bl_label = 'Pause Action'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseActionNode, category=MODULE_AS_CATEGORY)
