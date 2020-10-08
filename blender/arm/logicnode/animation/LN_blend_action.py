from arm.logicnode.arm_nodes import *

class BlendActionNode(ArmLogicTreeNode):
    """Interpolates between the two given actions."""
    bl_idname = 'LNBlendActionNode'
    bl_label = 'Blend Action'
    arm_version = 1

    def init(self, context):
        super(BlendActionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action 1')
        self.add_input('ArmNodeSocketAnimAction', 'Action 2')
        self.add_input('NodeSocketFloat', 'Factor', default_value = 0.5)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(BlendActionNode, category=PKG_AS_CATEGORY, section='action')
