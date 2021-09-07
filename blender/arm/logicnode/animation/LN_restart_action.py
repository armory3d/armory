from arm.logicnode.arm_nodes import *

class RestartActionNode(ArmLogicTreeNode):
    """Restarts the action"""
    bl_idname = 'LNRestartActionNode'
    bl_label = 'Restart Action'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action ID')
        
        self.add_output('ArmNodeSocketAction', 'Out')
