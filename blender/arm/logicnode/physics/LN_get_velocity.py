from arm.logicnode.arm_nodes import *

class GetVelocityNode(ArmLogicTreeNode):
    """Get velocity node"""
    bl_idname = 'LNGetVelocityNode'
    bl_label = 'Get Velocity'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Linear')
        # self.add_output('NodeSocketVector', 'Linear Factor') # TODO
        # self.outputs[-1].default_value = [1.0, 1.0, 1.0]
        self.add_output('NodeSocketVector', 'Angular')
        # self.add_output('NodeSocketVector', 'Angular Factor') # TODO
        # self.outputs[-1].default_value = [1.0, 1.0, 1.0]

add_node(GetVelocityNode, category=PKG_AS_CATEGORY)
