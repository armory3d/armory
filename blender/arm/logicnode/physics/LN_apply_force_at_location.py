from arm.logicnode.arm_nodes import *

class ApplyForceAtLocationNode(ArmLogicTreeNode):
    """Apply force at location node"""
    bl_idname = 'LNApplyForceAtLocationNode'
    bl_label = 'Apply Force At Location'
    arm_version = 1

    def init(self, context):
        super(ApplyForceAtLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('NodeSocketVector', 'Force')
        self.add_input('NodeSocketBool', 'Force On Local Axis')
        self.add_input('NodeSocketVector', 'Location')
        self.add_input('NodeSocketBool', 'Location On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyForceAtLocationNode, category=PKG_AS_CATEGORY, section='force')
