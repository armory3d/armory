from arm.logicnode.arm_nodes import *


class MapLoopNode(ArmLogicTreeNode):
    """Map Loop"""
    bl_idname = 'LNMapLoopNode'
    bl_label = 'Map Loop'
    arm_version = 1


    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Map')

        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('ArmDynamicSocket', 'Key')
        self.add_output('ArmDynamicSocket', 'Value')
        self.add_output('ArmNodeSocketAction', 'Done')
