from arm.logicnode.arm_nodes import *

class StopAgentNode(ArmLogicTreeNode):
    """Stop agent node"""
    bl_idname = 'LNStopAgentNode'
    bl_label = 'Stop Agent'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(StopAgentNode, category=PKG_AS_CATEGORY)
