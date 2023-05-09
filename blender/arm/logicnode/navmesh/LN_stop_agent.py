from arm.logicnode.arm_nodes import *

class StopAgentNode(ArmLogicTreeNode):
    """Stops the given NavMesh agent."""
    bl_idname = 'LNStopAgentNode'
    bl_label = 'Stop Agent'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketAction', 'Out')
