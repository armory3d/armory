from arm.logicnode.arm_nodes import *

class SubStringNode(ArmLogicTreeNode):
    """Sub string node"""
    bl_idname = 'LNSubStringNode'
    bl_label = 'Sub String'
    arm_version = 1

    def init(self, context):
        super(SubStringNode, self).init(context)
        self.add_output('NodeSocketString', 'String In')
        self.add_input('NodeSocketString', 'String Out')
        self.add_input('NodeSocketInt', 'Start')
        self.add_input('NodeSocketInt', 'End')

add_node(SubStringNode, category=PKG_AS_CATEGORY)
