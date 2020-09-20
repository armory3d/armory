from arm.logicnode.arm_nodes import *

class HasContactArrayNode(ArmLogicTreeNode):
    """Has contact array node"""
    bl_idname = 'LNHasContactArrayNode'
    bl_label = 'Has Contact Array'
    arm_version = 1

    def init(self, context):
        super(HasContactArrayNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('ArmNodeSocketArray', 'Rigid Bodies')
        self.add_output('NodeSocketBool', 'Has Contact')

add_node(HasContactArrayNode, category=PKG_AS_CATEGORY, section='contact')
