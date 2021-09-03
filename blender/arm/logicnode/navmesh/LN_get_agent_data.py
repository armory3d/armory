from arm.logicnode.arm_nodes import *

class GetAgentDataNode(ArmLogicTreeNode):
    """Gets the speed and turn duration of the agent"""
    bl_idname = 'LNGetAgentDataNode'
    bl_label = 'Get Agent Data'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmFloatSocket', 'Speed')
        self.add_output('ArmFloatSocket', 'Turn Duration')