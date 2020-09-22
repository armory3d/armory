from arm.logicnode.arm_nodes import *

class GetRigidBodyDataNode(ArmLogicTreeNode):
    """Get Rigid Body Data node"""
    bl_idname = 'LNGetRigidBodyDataNode'
    bl_label = 'Get Rigid Body Data'
    arm_version = 1

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Is Rigid Body')
        #self.outputs.new('NodeSocketString', 'Collision Shape')
        #self.outputs.new('NodeSocketInt', 'Activation State')
        self.outputs.new('NodeSocketInt', 'Collision Group')
        self.outputs.new('NodeSocketInt', 'Collision Mask')
        self.outputs.new('NodeSocketBool', 'Is Animated')
        self.outputs.new('NodeSocketBool', 'Is Static')
        self.outputs.new('NodeSocketFloat', 'Angular Damping')
        self.outputs.new('NodeSocketFloat', 'Linear Damping')
        self.outputs.new('NodeSocketFloat', 'Friction')
        self.outputs.new('NodeSocketFloat', 'Mass')

add_node(GetRigidBodyDataNode, category=PKG_AS_CATEGORY, section='props')
