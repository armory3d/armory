from arm.logicnode.arm_nodes import *

class ObjectNode(ArmLogicTreeNode):
    """Object node"""
    bl_idname = 'LNObjectNode'
    bl_label = 'Object'
    arm_version = 1

    def init(self, context):
        super(ObjectNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketObject', 'Object', is_var=True)

add_node(ObjectNode, category=PKG_AS_CATEGORY)
