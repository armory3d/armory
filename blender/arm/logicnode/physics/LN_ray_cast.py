from arm.logicnode.arm_nodes import *

class RayCastNode(ArmLogicTreeNode):
    """Cast physics ray node"""
    bl_idname = 'LNCastPhysicsRayNode'
    bl_label = 'Ray Cast'
    arm_version = 1

    def init(self, context):
        super(RayCastNode, self).init(context)
        self.add_input('NodeSocketVector', 'From')
        self.add_input('NodeSocketVector', 'To')
        self.add_input('NodeSocketInt', 'Collision Group Mask')
        self.add_output('ArmNodeSocketObject', 'Rigid Body')
        self.add_output('NodeSocketVector', 'Hit')
        self.add_output('NodeSocketVector', 'Normal')

add_node(RayCastNode, category=PKG_AS_CATEGORY, section='ray')
