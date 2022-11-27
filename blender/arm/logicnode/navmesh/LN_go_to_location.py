from arm.logicnode.arm_nodes import *

class GoToLocationNode(ArmLogicTreeNode):
    """Makes a NavMesh agent go to location."""
    bl_idname = 'LNGoToLocationNode'
    bl_label = 'Go to Location'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Location')
        self.add_input('ArmFloatSocket', 'Speed', 5.0)
        self.add_input('ArmFloatSocket', 'Turn Duration', 0.4)

        self.add_output('ArmNodeSocketAction', 'Out')

