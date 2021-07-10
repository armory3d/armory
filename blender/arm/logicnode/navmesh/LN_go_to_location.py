from arm.logicnode.arm_nodes import *

class GoToLocationNode(ArmLogicTreeNode):
    """Makes a NavMesh agent go to location."""
    bl_idname = 'LNGoToLocationNode'
    bl_label = 'Go to Location'
    arm_version = 1

    def init(self, context):
        super(GoToLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Location')

        self.add_output('ArmNodeSocketAction', 'Out')

