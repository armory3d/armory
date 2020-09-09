from arm.logicnode.arm_nodes import *

class GetDistanceNode(ArmLogicTreeNode):
    """Get distance node"""
    bl_idname = 'LNGetDistanceNode'
    bl_label = 'Get Distance'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketFloat', 'Distance')

add_node(GetDistanceNode, category=PKG_AS_CATEGORY)
