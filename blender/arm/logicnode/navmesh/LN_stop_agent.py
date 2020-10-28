from arm.logicnode.arm_nodes import *

class StopAgentNode(ArmLogicTreeNode):
    """Stops the given NavMesh agent."""
    bl_idname = 'LNStopAgentNode'
    bl_label = 'Stop Agent'
    arm_version = 1

    def init(self, context):
        super(StopAgentNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')
