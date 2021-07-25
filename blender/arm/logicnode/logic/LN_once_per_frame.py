from arm.logicnode.arm_nodes import *


class OncePerFrameNode(ArmLogicTreeNode):
    """Activates the output only once per frame if receives one or more inputs in that frame
    If there is no input, there will be no output"""
    bl_idname = 'LNOncePerFrameNode'
    bl_label = 'Once Per Frame'
    arm_section = 'flow'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
