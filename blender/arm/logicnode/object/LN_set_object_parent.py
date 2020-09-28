from arm.logicnode.arm_nodes import *

class SetParentNode(ArmLogicTreeNode):
    """Set the direct parent (nearest in the hierarchy) of an object.

    @seeNode Get Object Parent"""
    bl_idname = 'LNSetParentNode'
    bl_label = 'Set Object Parent'
    arm_version = 1

    def init(self, context):
        super(SetParentNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Parent', default_value='Parent')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetParentNode, category=PKG_AS_CATEGORY, section='relations')
