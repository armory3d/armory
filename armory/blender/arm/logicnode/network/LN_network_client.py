from arm.logicnode.arm_nodes import *


class NetworkClientNode(ArmLogicTreeNode):
    """Network client to connect to an existing host"""
    bl_idname = 'LNNetworkClientNode'
    bl_label = 'Create Client'
    arm_version = 1


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Url', default_value="ws://127.0.0.1:8001")

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Connection')
