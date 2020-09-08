from arm.logicnode.arm_nodes import *

class PlayActionNode(ArmLogicTreeNode):
    """Play action node"""
    bl_idname = 'LNPlayActionNode'
    bl_label = 'Play Action'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_input('NodeSocketFloat', 'Blend', default_value=0.2)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')

add_node(PlayActionNode, category=MODULE_AS_CATEGORY)
