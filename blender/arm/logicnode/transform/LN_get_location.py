from arm.logicnode.arm_nodes import *

class GetLocationNode(ArmLogicTreeNode):
    """Get location node"""
    bl_idname = 'LNGetLocationNode'
    bl_label = 'Get Location'
    arm_version = 1

    def init(self, context):
        super(GetLocationNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Location')

add_node(GetLocationNode, category=PKG_AS_CATEGORY, section='location')
